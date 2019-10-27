import math
import random
from datetime import datetime

from flask import jsonify, request
from haversine import haversine, Unit

from app import db, gmaps
from app.main import main
from app.models.user import User, Messages


@main.route("/")
def home():
    return "Server is up. LEGO LEGO"


@main.route("/add_message", methods=["POST"])
def add_message():
    data = request.json
    id = data["current_user_id"]
    other_user_id = data["requested_user_id"]
    msg = data["msg"]

    user = User.query.get(id)
    request_user = User.query.get(other_user_id)
    message = Messages(msg=msg, sender_id=user.id, receiver_id=request_user.id)
    db.session.add(message)
    db.session.commit()
    return jsonify({"status": 200, "msg": "Updated message"})


@main.route("/get_messages", methods=["POST"])
def message():
    data = request.json
    id = data["current_user_id"]
    other_user_id = data["current_user_id"]

    user = User.query.get(id)
    request_user = User.query.get(other_user_id)

    return jsonify({"messages": user.get_messages(request_user), "status": 200})


@main.route("/add_friend", methods=["POST", "GET"])
def add_friend():
    data = request.json
    id = data["current_user_id"]
    friend_username = data["friend"]

    user = User.query.get(id)
    friend = User.query.filter_by(username=friend_username).first()

    user.follow(friend)
    friend.follow(user)
    db.session.commit()
    return jsonify({"status": 200, "msg": "added friend"})


def calc_haversine(current_user, user):
    if current_user.lat is None or user.lat is None:
        return -1
    return haversine((current_user.lat, current_user.lon), (
        user.lat, user.lon), unit=Unit.MILES)


@main.route("/get_all_users", methods=["POST"])
def friends():
    data = request.json
    id = data["current_user_id"]
    current_user = User.query.get(id)
    if current_user is None:
        return jsonify({"friends": []})
    users = User.query.all()
    if "friends" in data:
        users = current_user.followed.all()
    return jsonify({"friends": [{"username": user.username,
                                 "id": user.id,
                                 "lat": user.lat,
                                 "lon": user.lon,
                                 "dist": calc_haversine(user, current_user),
                                 "image": user.image} for user in users if user and user.id != current_user.id]})


@main.route("/create_user", methods=["POST", "GET"])
def create_user():
    data = request.json
    username = data["username"]
    if username == "":
        return jsonify({"id": -1, "status": 200})
    phone_number = data["phone_number"]
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    user = User(username=username, phone_number=phone_number)

    rand_ind, gender = random.randint(0, 99), random.randint(0, 1)
    if gender == 1:
        url = "https://randomuser.me/api/portraits/thumb/men/" + str(rand_ind) + ".jpg"
    else:
        url = "https://randomuser.me/api/portraits/thumb/women/" + str(rand_ind) + ".jpg"

    user.image = url

    db.session.add(user)
    db.session.commit()

    return jsonify({"id": user.id, "status": 200})


@main.route("/save_user_loc", methods=["POST", "GET"])
def save_user_loc():
    data = request.json

    id = data["current_user_id"]
    lat = data["current_user_lat"]
    lon = data["current_user_long"]

    user = User.query.get(id)
    if user is None:
        return jsonify({"status": 300, "msg": "User not initialized to a valid person"})

    user.lat = float(lat)
    user.lon = float(lon)
    db.session.commit()
    return jsonify({"status": 200, "msg": "Received user's location"})


@main.route("/request_user_loc", methods=["POST", "GET"])
def request_user_loc():
    data = request.json
    id = data["current_user_id"]
    lat = data["current_user_lat"]
    lon = data["current_user_long"]

    user = User.query.get(id)
    user.lat = float(lat)
    user.lon = float(lon)
    db.session.commit()

    id = data["requested_user_id"]
    requested_user = User.query.get(id)

    return {"requested_user_lat": requested_user.lat,
            "requested_user_long": requested_user.lon,
            "bearing": calc_bearing(user.lat, user.lon, requested_user.lat, requested_user.lon),
            "dist": calc_haversine(user, requested_user)}


@main.route("/get_path", methods=["POST"])
def get_path():
    """
     {
         "distance" : {
            "text" : "0.4 mi",
            "value" : 609
         },
         "duration" : {
            "text" : "3 mins",
            "value" : 160
         },
         "end_location" : {
            "lat" : 33.8054699,
            "lng" : -117.9267488
         },
         "start_location" : {
            "lat" : 33.80545170000001,
            "lng" : -117.9242185
         },
      },
    """
    data = request.json
    id = data["current_user_id"]
    user = User.query.get(id)

    id = data["requested_user_id"]
    r_user = User.query.get(id)

    convert_dict = lambda x, y: {"lat": x, "lng": y}
    directions_result = gmaps.directions(convert_dict(user.lat, user.lon),
                                         convert_dict(r_user.lat, r_user.lon),
                                         mode="walking",
                                         departure_time=datetime.now())
    if not directions_result:
        return jsonify({"status": 400})

    leg = directions_result[0]["legs"][0]
    total_distance = leg["distance"]["text"]
    total_eta = leg["duration"]["text"]
    steps = leg["steps"]

    return jsonify({"total_distance": total_distance, "total_eta": total_eta, "steps": steps, "landmarks": []})


def calc_bearing(lat1, lon1, lat2, lon2):
    startLat = math.radians(lat1)
    startLong = math.radians(lon1)
    endLat = math.radians(lat2)
    endLong = math.radians(lon2)

    dLong = endLong - startLong

    dPhi = math.log(math.tan(endLat / 2.0 + math.pi / 4.0) / math.tan(startLat / 2.0 + math.pi / 4.0))
    if abs(dLong) > math.pi:
        if dLong > 0.0:
            dLong = -(2.0 * math.pi - dLong)
        else:
            dLong = (2.0 * math.pi + dLong)

    bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0

    return bearing
