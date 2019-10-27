import math
from datetime import datetime

from flask import jsonify, request

from app import db, gmaps
from app.main import main
from app.models.user import User


@main.route("/")
def home():
    return "Server is up. LEGO LEGO"


@main.route("/add_friend")
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


@main.route("/get_all_users")
def friends():
    data = request.json
    id = data["current_user_id"]
    users = User.query.all()
    if "friends" in data:
        user = User.query.get(id)
        users = user.followed.all()
    return jsonify({"friends": [{"username": user.username,
                                 "id": user.id,
                                 "lat": user.lat,
                                 "lon": user.lon} for user in users if user.id != id]})


@main.route("/create_user", methods=["POST", "GET"])
def create_user():
    data = request.json
    username = data["username"]
    phone_number = data["phone_number"]
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
    user = User(username=username, phone_number=phone_number)
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
        return jsonify({"status": 200, "msg": "User not initialized to a valid person"})

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
            "bearing": calc_bearing(user.lat, user.lon, requested_user.lat, requested_user.lon)}


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
    return jsonify({"total_distance": total_distance, "total_eta": total_eta, "steps": steps})


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

    bearing = (math.degrees(math.atan2(dLong, dPhi)) + 360.0) % 360.0;

    return bearing
