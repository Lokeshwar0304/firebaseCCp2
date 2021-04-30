from google.api_core import retry
from google.cloud import pubsub_v1
import os, json, math, redis, datetime
from firebase_admin import credentials, firestore, initialize_app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
    os.path.abspath(os.getcwd()) + "/key.json"
)

publisher = pubsub_v1.PublisherClient()
publisher.delete_topic(
    request={"topic": "projects/bloodbankasaservice/topics/AB-~0zKW8LM7Vfhc8EODUnjM"}
)
