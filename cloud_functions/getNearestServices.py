import json
from firebase_admin import credentials, firestore, initialize_app

cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
users = db.collection("User")
responses = db.collection("Response")


def get_nearest_services(request):
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

    # Set CORS headers for the main request
    headers = {"Access-Control-Allow-Origin": "*"}

    # if request.args:
    #     requestId = request.args.get('fetchId')
    print(request)
    request_json = request.get_json()
    print(request_json)
    requestId = request_json["fetchId"]
    doc_ref = responses.document(requestId)
    if doc_ref:
        doc = doc_ref.get()
        if doc.exists:
            doc = doc.to_dict()
            responseObj = {}
            responseObj["requestEmail"] = doc["requestEmail"]
            for provider in list(doc["response"].keys()):
                email = list(doc["response"][provider].keys())[0]
                if email:
                    hospitals = users.where("email", "==", email).stream()
                    for hosp in hospitals:
                        hosp = hosp.to_dict()
                        responseObj[provider] = {
                            **{
                                key: hosp[key]
                                for key in hosp.keys()
                                if key not in ["bloodGroupQuan", "userType", "photoURL"]
                            },
                            **{"distance": doc["response"][provider][email]},
                        }
            return (json.dumps(responseObj), 200, headers)
    else:
        return (f"No such document!", 200, headers)
