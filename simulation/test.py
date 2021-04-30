import os
from google.cloud import pubsub_v1
from google.api_core import retry


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
project_id = "bloodbankasaservice"

topic_id = "vinay"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)
# topic = publisher.create_topic(request={"name": topic_path})


def callback(message):
    message.ack()
    print(message.data)
    return message.data


def subscribe():
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, "vinay")
    # subscriber.create_subscription(
    #     request={"name": subscription_path, "topic": topic_path}
    # )
    NUM_MESSAGES = 1
    with subscriber:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": NUM_MESSAGES},
            retry=retry.Retry(deadline=10),
        )

        ack_ids = []
        if response.received_messages:
            received_message = response.received_messages[0]
            ack_ids.append(received_message.ack_id)
            subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": ack_ids}
            )
            return received_message.message.data
        return "no response"


print(subscribe())

# publisher.delete_topic(request={"topic": topic_path})