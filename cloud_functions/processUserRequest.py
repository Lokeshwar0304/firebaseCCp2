from firebase_admin import credentials, firestore, initialize_app
from math import radians, cos, sin, asin, sqrt

cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
users = db.collection("User")
responses = db.collection("Response")


def distance(lat1, lat2, lon1, lon2):

    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2

    c = 2 * asin(sqrt(a))

    # Radius of earth in kilometers. Use 3956 for miles and 6371 for km
    r = 3956

    return c * r


def process_user_request(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    resource_string = context.resource
    if event and event["value"]["fields"]["email"]:
        response = dict()
        response["response"] = dict()
        response["requestId"] = (
            resource_string.split("/")[-1] if resource_string else None
        )
        nearest_hospitals, nearest_banks = {}, {}
        request_email = event["value"]["fields"]["email"]["stringValue"]
        response["requestEmail"] = request_email
        request_lat = event["value"]["fields"]["latitude"]["doubleValue"]
        request_long = event["value"]["fields"]["longitude"]["doubleValue"]
        docs = (
            users.where(u"userType", u"==", "USER")
            .where(u"email", u"==", request_email)
            .stream()
        )
        for doc in docs:
            doc = doc.to_dict()
            request_bloodgroup = doc["bloodGroup"]
        # Nearest Hospital
        hospitals = users.where(u"userType", u"==", "HOSPITAL").stream()
        for hospital in hospitals:
            hospital = hospital.to_dict()
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
        response["response"]["hospital"] = nearest_hospitals
        # Nearest Hospital
        bloodbanks = users.where(u"userType", u"==", "BLOOD BANK").stream()
        for bloodbank in bloodbanks:
            bloodbank = bloodbank.to_dict()
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
        response["response"]["bloodBank"] = nearest_banks
        res = responses.document(response["requestId"])
        res.set(response, merge=True)
        print(response)
