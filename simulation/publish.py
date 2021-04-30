import os
from google.cloud import pubsub_v1

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
project_id = "bloodbankasaservice"


def publish():
    topic_id = "vinay"
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    future = publisher.publish(topic_path, "hello".encode("utf-8"))
    return future.result()


print(publish())