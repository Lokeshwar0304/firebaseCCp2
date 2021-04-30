# https://us-central1-bloodbankasaservice.cloudfunctions.net/get_blood_request

from google.api_core import retry
from google.cloud import pubsub_v1
import os, json, math, redis, datetime
from firebase_admin import credentials, firestore, initialize_app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    os.path.abspath(os.getcwd()) + "/key.json"
)

timeout = 180
project_id = "bloodbankasaservice"
cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
user_db = db.collection("User")
request_db = db.collection("Request")
redis_host = "10.0.0.3"
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)


def get_user(user_id):
    user = user_db.document(user_id).get().to_dict()
    return user


def get_request(request_id):
    request = request_db.document(request_id).get().to_dict()
    user = user_db.document(request["victim_id"]).get().to_dict()
    user["coordinates"] = {
        "longitude": request["longitude"],
        "latitude": request["latitude"],
    }
    return user


def response(message):
    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    return (message, 200, headers)


def get_blood_request(request):
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
    user_id = request_json["user_id"]
    request_id = request_json["request_id"]

    donor = get_user(user_id)
    receiver = get_request(request_id)
    data = {"donar": donor, "receiver": receiver}
    return response(json.dumps(data))
