# https://us-central1-bloodbankasaservice.cloudfunctions.net/get_user_by_request

from google.api_core import retry
from google.cloud import pubsub_v1
import os, json, math, redis, datetime
from firebase_admin import credentials, firestore, initialize_app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    os.path.abspath(os.getcwd()) + "/key.json"
)

timeout = 300
project_id = "bloodbankasaservice"
cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
user = db.collection("User")
request = db.collection("Request")
redis_host = "10.0.0.3"
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)


class Blood_Request:
    def __init__(self, victim_id, blood_group, timestamp, latitude, longitude):
        self.victim_id = victim_id
        self.blood_group = blood_group
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude


# TODO need to update the face_signature
def find_victim(victim_id, face_signature: str):
    # TODO match the face
    # victim_id = "0zKW8LM7Vfhc8EODUnjM"
    doc = user.document(victim_id).get().to_dict()
    blood_group = doc["bloodGroup"]
    return victim_id, blood_group


def get_time_diff(old, new):
    return (
        (
            datetime.datetime.fromtimestamp(round(new / 1000))
            - datetime.datetime.fromtimestamp(round(old / 1000))
        ).seconds
    ) / (60)


def get_within_radius(old_latitude, old_longitude, new_latitude, new_longitude):
    R = 6373.0
    lat1 = math.radians(old_latitude)
    lon1 = math.radians(old_longitude)
    lat2 = math.radians(new_latitude)
    lon2 = math.radians(new_longitude)
    longitude_diff = lon2 - lon1
    latitude_diff = lat2 - lat1
    a = (
        math.sin(latitude_diff / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(longitude_diff / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


def check_duplicate_request(blood_request: Blood_Request):
    key = f"{blood_request.blood_group}~{blood_request.victim_id}"
    value = redis_client.get(key)
    if not value:
        return False
    old = json.loads(value, object_hook=lambda d: Blood_Request(**d))
    time_diff = get_time_diff(old.timestamp, blood_request.timestamp)
    within_radius = get_within_radius(
        old.latitude, old.longitude, blood_request.latitude, blood_request.longitude
    )
    if time_diff < timeout / 60 and within_radius < 2:
        return True
    return False


def clear_cache(blood_request: Blood_Request):
    key = f"{blood_request.blood_group}~{blood_request.victim_id}"
    redis_client.delete(key)
    return True


# TODO error handling
def push_request_to_queue(blood_request: Blood_Request):
    topic = f"{ blood_request.blood_group.lower() }blood_group"
    publisher = pubsub_v1.PublisherClient()
    topic_name = f"projects/{project_id}/topics/{topic}"
    generic_topic_name = f"projects/{project_id}/topics/generic_blood_group"
    message = json.dumps(blood_request.__dict__)
    future = publisher.publish(topic_name, str.encode(message))
    future.result()
    future = publisher.publish(generic_topic_name, str.encode(message))
    future.result()
    return True


# TODO error handling
def update_cache(blood_request: Blood_Request):
    key = f"{blood_request.blood_group}~{blood_request.victim_id}"
    redis_client.set(key, json.dumps(blood_request.__dict__))
    return True


# TODO error handling
def update_storage(blood_request: Blood_Request):
    key = f"{blood_request.blood_group}~{blood_request.victim_id}"
    request.document(key).set(blood_request.__dict__)
    return True


def create_topic(blood_request: Blood_Request):
    topic_id = f"{blood_request.blood_group}~{blood_request.victim_id}"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    topic = publisher.create_topic(request={"name": topic_path})
    return topic.name


def delete_topic(blood_request: Blood_Request, topic_path: str):
    publisher = pubsub_v1.PublisherClient()
    publisher.delete_topic(request={"topic": topic_path})
    clear_cache(blood_request)
    return True


def listen_topic(blood_request: Blood_Request, topic_path: str):
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, f"{blood_request.blood_group}~{blood_request.victim_id}"
    )
    subscriber.create_subscription(
        request={"name": subscription_path, "topic": topic_path}
    )
    final_response = "No donor is ready :("
    with subscriber:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": 1},
            retry=retry.Retry(deadline=180),
        )
        ack_ids = []
        if response.received_messages:
            received_message = response.received_messages[0]
            ack_ids.append(received_message.ack_id)
            subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": ack_ids}
            )
            name, email = received_message.message.data.decode("utf-8").split("~")
            final_response = f"{name} wants to donate! His email is {email}"
        delete_topic(blood_request, topic_path)
        subscriber.delete_subscription(request={"subscription": subscription_path})
        return final_response


def response(message):
    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    return (message, 200, headers)


def got_blood_request(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """

    if request.method == "OPTIONS":
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Max-Age": "3600",
        }
        return ("", 204, headers)

    print(request)
    request_json = request.get_json()
    print(request_json)
    victim_id = request_json["victim_id"]
    blood_group = None
    timestamp = request_json["timestamp"]
    latitude = request_json["latitude"]
    longitude = request_json["longitude"]

    if request_json["anonymous"]:
        face_signature = request_json["face_signature"]
        victim_id, blood_group = find_victim(victim_id, face_signature)
    else:
        victim_id = request_json["victim_id"]
        blood_group = request_json["blood_type"]

    if not blood_group:
        return response("Victim is not recognized!")

    blood_request = Blood_Request(
        victim_id, blood_group, timestamp, latitude, longitude
    )

    if check_duplicate_request(blood_request):
        return response("Victim was already takencare of.")

    # TODO create topic for the request
    topic_path = create_topic(blood_request)
    queue_success = push_request_to_queue(blood_request)
    if queue_success:
        cache_success = update_cache(blood_request)
        if cache_success:
            storage_success = update_storage(blood_request)
            if storage_success:
                payload = listen_topic(blood_request, topic_path)
                return response(payload)
            else:
                # need to revert
                delete_topic(blood_request, topic_path)
                return response("Storing failed!")
        else:
            # need to revert
            delete_topic(blood_request, topic_path)
            return response("Caching failed!")
    else:
        delete_topic(blood_request, topic_path)
        return response("Raising request failed!")
