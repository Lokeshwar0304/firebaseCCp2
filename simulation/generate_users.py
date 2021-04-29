import requests
import random
import math

from collections import Counter
from tqdm import tqdm
from firebase_admin import credentials, firestore, initialize_app
import concurrent.futures

project_id = "bloodbankasaservice"
cred = credentials.Certificate("./key.json")
default_app = initialize_app(cred)
db = firestore.client()
user_db = db.collection("User")


def random_close_coord(lat=33.409566, lng=-111.9206614):
    r = (310000) / 111300
    u = random.uniform(0, 1)
    v = random.uniform(0, 1)
    w = r * math.sqrt(u)
    t = 2 * math.pi * v
    x = w * math.cos(t)
    y1 = w * math.sin(t)
    x1 = x / math.cos(lng)
    new_lng = lng + y1
    new_lat = lat + x1
    return new_lat, new_lng


def get_radom_user():

    blood_groups = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    userType = ["USER"] * 7 + ["HOSPITAL"] * 2 + ["BLOOD BANK"]

    data = None
    try:
        data = requests.get("https://randomuser.me/api/").json()
    except (e):
        print(e)

    data = data["results"][0]
    latitude, longitude = random_close_coord()
    ut = random.choice(userType)
    user = None
    contact = data["phone"]
    address = (
        str(data["location"]["street"]["number"])
        + ", "
        + data["location"]["street"]["name"]
        + ", "
        + data["location"]["city"]
        + ", "
        + data["location"]["state"]
        + ", "
        + data["location"]["country"]
        + ", "
        + str(data["location"]["postcode"])
    )
    if ut == "USER":
        user = {
            "firstName": data["name"]["first"],
            "lastName": data["name"]["last"],
            "displayName": f"{data['name']['first']} {data['name']['last']}",
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "email": data["email"],
            "bloodGroup": random.choice(blood_groups),
            "photoURL": None,
            "userType": ut,
            "address": address,
            "contact": contact,
        }
    else:
        user = {
            "displayName": f"{data['name']['first']} {data['name']['last']}",
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "email": data["email"],
            "photoURL": None,
            "userType": ut,
            "address": address,
            "contact": contact,
            "bloodGroupQuan": [(bg, random.randint(0, 20)) for bg in blood_groups],
        }

    user_db.add(user)


# def looper(l):
#     get_radom_user()


# with concurrent.futures.ThreadPoolExecutor(max_workers=70) as executor:
#     tqdm(executor.map(looper, range(700000)), total=len(700000))


# 700000
# count = 0
# for doc in user_db.stream():
#     count += 1
# print(count)