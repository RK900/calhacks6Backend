from flask import jsonify, request

from app import db
from app.main import main
from app.models.user import User
import googlemaps
from datetime import datetime


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
    user.lat = lat
    user.lon = lon
    db.session.commit()
    return jsonify({"status": 200})


@main.route("/request_user_loc", methods=["POST", "GET"])
def request_user_loc():
    data = request.json
    id = data["current_user_id"]
    lat = data["current_user_lat"]
    lon = data["current_user_long"]

    user = User.query.get(id=id)
    user.lat = lat
    user.lon = lon
    db.session.commit()

    id = data["requested_user_id"]
    requested_user = User.query.get(id=id)

    return {"requested_user_lat": requested_user.current_user_lat,
            "requested_user_long": requested_user.current_user_long}


@main.route("/get_path")
def get_path():
    data = request.json

    gmaps = googlemaps.Client(key='Add Your Key here')

    # Geocoding an address
    geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

    # Look up an address with reverse geocoding
    reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

    # Request directions via public transit
    now = datetime.now()
    directions_result = gmaps.directions("Sydney Town Hall",
                                         "Parramatta, NSW",
                                         mode="transit",
                                         departure_time=now)
