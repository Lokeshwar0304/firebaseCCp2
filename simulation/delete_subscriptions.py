from google.cloud import pubsub_v1
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./key.json"
project_id = "bloodbankasaservice"


# NOTE this is to clear the subscriptions
print("Cleaning subscriptions...")
subscriber = pubsub_v1.SubscriberClient()
project_path = f"projects/{project_id}"
with subscriber:
    for subscription in subscriber.list_subscriptions(
        request={"project": project_path}
    ):
        print(subscription.name)
        subscriber.delete_subscription(request={"subscription": subscription.name})