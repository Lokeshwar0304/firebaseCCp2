import os, sys
import json
import threading, contextlib
from google.cloud import pubsub_v1
from helper import Blood_Request, get_within_radius
from firebase_admin import credentials, firestore, initialize_app

number_of_users = int(sys.argv[1]) if len(sys.argv) > 1 else 10
starts_with = sys.argv[2] if len(sys.argv) > 2 else "a"


def callback(message, user):
    blood_request = json.loads(
        message.data.decode("utf-8"), object_hook=lambda d: Blood_Request(**d)
    )
    distance = get_within_radius(
        user["coordinates"]["latitude"],
        user["coordinates"]["longitude"],
        blood_request.latitude,
        blood_request.longitude,
    )
    with open("available_users", "a") as f:
        f.write(
            f"{user['user_id']} ({user['displayName']}) -> {blood_request.victim_id} : {str(distance)}\n"
        )
    if distance < 300:
        with open("close_users", "a") as f:
            f.write(
                f"{distance} : http://localhost:3000/notified/{user['user_id']}/{blood_request.blood_group}~{blood_request.victim_id}\n"
            )

    message.ack()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"

project_id = "bloodbankasaservice"
cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
user_db = db.collection("User")

subscriber_shutdown = threading.Event()
subscribers = []
streaming_pull_futures = []
user_dicts = []

print("\nStarted simulation...")
with open("available_users", "w") as f:
    f.write("Avialable users Listening:\n")
with open("close_users", "w") as f:
    f.write("Closest users Listening:\n")

user_stream = user_db.stream()
for user in user_stream:
    if number_of_users == 0:
        break
    user_dict = user.to_dict()
    if (
        user_dict
        and "displayName" in user_dict
        and user_dict["displayName"]
        and user_dict["displayName"][0].lower() == starts_with
        and all(ord(char) < 128 for char in user_dict["displayName"])
    ):
        user_dict["user_id"] = user.id
        user_dicts.append(user_dict)
        number_of_users -= 1


def subscribe(i, user_dicts):
    if i >= len(user_dicts):
        return
    user_dict = user_dicts[i]
    if "bloodGroup" in user_dict:
        topic = f"{ user_dict['bloodGroup'].lower() }blood_group"
        topic_name = f"projects/{project_id}/topics/{topic}"
        sub_name = f"projects/{project_id}/subscriptions/{user_dict['displayName'].replace(' ', '_')+ '_'+ user_dict['bloodGroup']}"
    else:
        topic = f"generic_blood_group"
        topic_name = f"projects/{project_id}/topics/{topic}"
        sub_name = f"projects/{project_id}/subscriptions/{user_dict['displayName'].replace(' ', '_')+ '_generic'}"
    subscriber = pubsub_v1.SubscriberClient()
    # subscriber.create_subscription(request={"name": sub_name, "topic": topic_name})
    streaming_pull_future = subscriber.subscribe(
        sub_name, callback=lambda msg: callback(msg, user_dict)
    )
    streaming_pull_future.add_done_callback(lambda result: subscriber_shutdown.set())
    print(f"Ready: {sub_name}")
    subscribe(i + 1, user_dicts)
    subscribers.append(subscriber)
    streaming_pull_futures.append(streaming_pull_future)


subscribe(0, user_dicts)
print("\nSimulation Ready...")

with contextlib.ExitStack() as stack:
    files = [stack.enter_context(s) for s in subscribers]
    subscriber_shutdown.wait()
    for streaming_pull_future in streaming_pull_futures:
        streaming_pull_future.cancel()