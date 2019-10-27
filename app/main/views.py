from datetime import datetime

from flask import jsonify, request

from app import db, gmaps
from app.main import main
from app.models.user import User


@main.route("/")
def home():
    return "Server is up. LEGO LEGO"


@main.route("/get_all_users")
def friends():
    users = User.query.all()
    return jsonify({"friends": [{"username": user.username,
                                 "id": user.id,
                                 "lat": user.lat,
                                 "lon": user.lon} for user in users]})


@main.route("/create_user", methods=["POST", "GET"])
def create_user():
    data = request.json
    username = data["username"]
    phone_number = data["phone_number"]

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

    user = User.query.get(id=id)
    user.lat = float(lat)
    user.lon = float(lon)
    db.session.commit()
    return jsonify({"status": 200})


@main.route("/request_user_loc", methods=["POST", "GET"])
def request_user_loc():
    data = request.json
    id = data["current_user_id"]
    lat = data["current_user_lat"]
    lon = data["current_user_long"]

    user = User.query.get(id=id)
    user.lat = float(lat)
    user.lon = float(lon)
    db.session.commit()

    id = data["requested_user_id"]
    requested_user = User.query.get(id=id)

    return {"requested_user_lat": requested_user.current_user_lat,
            "requested_user_long": requested_user.current_user_long}


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
         "html_instructions" : "Head \u003cb\u003ewest\u003c/b\u003e toward \u003cb\u003eDisneyland Dr\u003c/b\u003e",
         "start_location" : {
            "lat" : 33.80545170000001,
            "lng" : -117.9242185
         },
      },
    """
    data = request.json
    id = data["current_user_id"]
    user = User.query.get(id=id)

    id = data["requested_user_id"]
    r_user = User.query.get(id=id)

    convert_dict = lambda x, y: {"lat": x, "lng": y}
    directions_result = gmaps.directions(convert_dict(user.lat, user.long),
                                         convert_dict(r_user.lat, r_user.long),
                                         mode="walking",
                                         departure_time=datetime.now())
    if not directions_result:
        return jsonify({"status": 400})

    leg = directions_result[0]
    total_distance = leg["distance"]["text"]
    total_eta = leg["duration"]["text"]
    steps = leg["steps"]
    return jsonify({"total_distance": total_distance, "total_eta": total_eta, "steps": steps})
