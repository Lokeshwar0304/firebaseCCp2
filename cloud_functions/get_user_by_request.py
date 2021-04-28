# https://us-central1-bloodbankasaservice.cloudfunctions.net/get_user_by_request

from firebase_admin import credentials, firestore, initialize_app
import redis
import math
import json
import datetime
from google.cloud import pubsub_v1
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    os.path.abspath(os.getcwd()) + "/key.json"
)

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
def find_victim(face_signature: str):
    # TODO match the face
    victim_id = "7HWiG7KSSjRhfzNYkcQ7tJDZisP2"
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
    key = f"{blood_request.victim_id}${blood_request.blood_group}"
    value = redis_client.get(key)
    if not value:
        return False
    old = json.loads(value, object_hook=lambda d: Blood_Request(**d))
    time_diff = get_time_diff(old.timestamp, blood_request.timestamp)
    within_radius = get_within_radius(
        old.latitude, old.longitude, blood_request.latitude, blood_request.longitude
    )
    if time_diff < 15 and within_radius < 2:
        return True
    return False


# TODO error handling
def push_request_to_queue(blood_request: Blood_Request):
    topic = f"{ blood_request.blood_group.lower() }blood_group"
    publisher = pubsub_v1.PublisherClient()
    topic_name = f"projects/{project_id}/topics/{topic}"
    message = json.dumps(blood_request.__dict__)
    future = publisher.publish(topic_name, str.encode(message))
    future.result()
    return True


# TODO error handling
def update_cache(blood_request: Blood_Request):
    key = f"{blood_request.victim_id}${blood_request.blood_group}"
    redis_client.set(key, json.dumps(blood_request.__dict__))
    return True


# TODO error handling
def update_storage(blood_request: Blood_Request):
    key = f"{blood_request.victim_id}${blood_request.blood_group}"
    request.document(key).set(blood_request.__dict__)
    return True


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
    victim_id = None
    blood_group = None
    timestamp = request_json["timestamp"]
    latitude = request_json["latitude"]
    longitude = request_json["longitude"]

    if request_json["anonymous"]:
        face_signature = request_json["face_signature"]
        victim_id, blood_group = find_victim(face_signature)
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

    queue_success = push_request_to_queue(blood_request)
    if queue_success:
        cache_success = update_cache(blood_request)
        if cache_success:
            storage_success = update_storage(blood_request)
            if storage_success:
                return response("You are a saviour! Help is on the way.")
            else:
                # need to revert
                return response("Storing failed!")
        else:
            # need to revert
            return response("Caching failed!")
    else:
        return response("Raising request failed!")
