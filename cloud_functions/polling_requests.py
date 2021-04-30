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


def listen_topic(blood_group, user_id):
    topic = f"{ blood_group.lower() }blood_group"
    topic_path = f"projects/{project_id}/topics/{topic}"
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(
        project_id, f"{blood_group}~{user_id}~temp"
    )
    subscriber.create_subscription(
        request={"name": subscription_path, "topic": topic_path}
    )
    final_response = None
    with subscriber:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": 1},
            retry=retry.Retry(deadline=10),
        )
        ack_ids = []
        if response.received_messages:
            received_message = response.received_messages[0]
            ack_ids.append(received_message.ack_id)
            subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": ack_ids}
            )
            final_response = received_message.message.data.decode("utf-8")
        subscriber.delete_subscription(request={"subscription": subscription_path})
        return final_response


def response(message):
    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    return (message, 200, headers)


def polling_requests(request):
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

    blood_group = request_json["blood_group"]
    user_id = request_json["user_id"]
    return response(listen_topic(blood_group, user_id))
