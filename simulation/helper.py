import math
import json

# NOTE blood request representation
class Blood_Request:
    def __init__(self, victim_id, blood_group, timestamp, latitude, longitude):
        self.victim_id = victim_id
        self.blood_group = blood_group
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude


def get_within_radius(old_latitude, old_longitude, new_latitude, new_longitude):
    R = 6373.0
    lat1 = math.radians(old_latitude)
    lon1 = math.radians(old_longitude)
    lat2 = math.radians(new_latitude)
    lon2 = math.radians(new_longitude)
    longitude_diff = lon2 - lon1
    latitude_diff = lat2 - lat1
    a = (
        math.sin(latitude_diff / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(longitude_diff / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


if __name__ == "__main__":
    pass