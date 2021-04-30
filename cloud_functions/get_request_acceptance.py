# https://us-central1-bloodbankasaservice.cloudfunctions.net/get_blood_request

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
user_db = db.collection("User")
request_db = db.collection("Request")
redis_host = "10.0.0.3"
redis_port = 6379
redis_client = redis.Redis(host=redis_host, port=redis_port)


def distance(lat1, lat2, lon1, lon2):

    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles and 6371 for km
    r = 3956

    return c * r


def get_user(user_id):
    user = user_db.document(user_id).get().to_dict()
    return user


def update_user(user_id, request_id):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, request_id)
    user = get_user(user_id)
    user_name = user["displayName"]
    email = user["email"]
    future = publisher.publish(topic_path, str.encode(user_name + "~" + email))
    future.result()
    return user


def response(message):
    headers = {
        "Access-Control-Allow-Origin": "*",
    }
    return (message, 200, headers)


def get_request_acceptance(request):
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
    # request_json = json.loads(request) 
    print(request_json)
    user_id = request_json["user_id"]
    request_id = request_json["request_id"]
    accepted = request_json["accepted"]
    if not accepted:
        return response(json.dumps({}))
    donor = update_user(user_id, request_id)
    locations = request_json["locations"]
    request_lat, request_long = (
        locations[1]["location"]["lat"],
        locations[1]["location"]["lng"],
    )
    request_bloodgroup = donor["bloodGroup"]
    nearest_hospitals, nearest_banks = {}, {}
    # Nearest Hospital
    respo = dict()
    hospitals = user_db.where(u"userType", u"==", "HOSPITAL").stream()
    hd = {}
    for hospital in hospitals:
        hospital = hospital.to_dict()
        hd[hospital["email"]] = [
            hospital["coordinates"]["lat"],
            hospital["coordinates"]["lng"],
        ]
        if (
            next(
                int(quan["quantity"])
                for quan in hospital["bloodGroupQuan"]
                if quan["itemName"] == request_bloodgroup
            )
            > 0
        ):
            curr_distance = distance(
                request_lat,
                hospital["coordinates"]["lat"],
                request_long,
                hospital["coordinates"]["lng"],
            )
            nearest_hospitals[hospital["email"]] = curr_distance
    nearest_hospitals = dict(
        sorted(nearest_hospitals.items(), key=lambda x: x[1], reverse=False)[:1]
    )
    respo["hospital"] = hd[(list(nearest_hospitals.keys()))[0]]
    # Nearest Hospital
    bloodbanks = user_db.where(u"userType", u"==", "BLOOD BANK").stream()
    bbd = {}
    for bloodbank in bloodbanks:
        bloodbank = bloodbank.to_dict()
        bbd[bloodbank["email"]] = [
            bloodbank["coordinates"]["lat"],
            bloodbank["coordinates"]["lng"],
        ]
        if (
            next(
                int(quan["quantity"])
                for quan in bloodbank["bloodGroupQuan"]
                if quan["itemName"] == request_bloodgroup
            )
            > 0
        ):
            curr_distance = distance(
                request_lat,
                bloodbank["coordinates"]["lat"],
                request_long,
                bloodbank["coordinates"]["lng"],
            )
            nearest_banks[bloodbank["email"]] = curr_distance
    nearest_banks = dict(
        sorted(nearest_banks.items(), key=lambda x: x[1], reverse=False)[:1]
    )
    respo["bloodBank"] = bbd[(list(nearest_banks.keys()))[0]]
    return response(respo)
