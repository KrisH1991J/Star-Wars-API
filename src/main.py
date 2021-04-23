"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, People, Planets, Starships

from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "JWT_SECRET_KEY"
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# @app.route("/create-token", methods=["POST"])
# def login():
#     user_id = 1
#     access_token = create_access_token(identity=user_id)
#     return jsonify(access_token=access_token)

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/signup", methods=["POST"])
def signup():
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)

    user_name = body["user_name"]
    user_name_exists = User.query.filter_by(user_name=user_name)

    if user_name is not None:
        raise APIException("The username you have selected is already taken", status_code=400)

    email = body["email"]
    email_exists = User.query.filter_by(email=email)

    if email_exists is not None:
        raise APIException("That email already exists", status_code=400)

    new_user = User(user_name=body["user_name"], first_name=body["first_name"], last_name=body["last_name"], email=body['email'], password=body['password'])
    db.session.add(new_user)
    db.session.commit()
    user_id = new_user.id
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token), 200

@app.route("/login", methods=["POST"])
def user_login():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    user = User.query.filter_by(email=email, password=password).first

    if user is None:
        raise APIException("Bad email or password", status_code=400)

    user_id = user.id
    access_token = create_access_token(identity=user_id)
    return jsonify(access_token=access_token), 200

@app.route("/user/<int:user_id>", methods=["DELETE"])
def del_user(user_id):
    sel_user = User.query.get(user_id)
    if sel_user is None:
        raise APIException("User not found", status_code=404)
    db.session.delete(sel_user)
    db.session.commit()

    return jsonify("ok"), 200

@app.route('/user', methods=['GET'])
def get_users():
    user_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), user_query))
    return jsonify(all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize()), 200

@app.route('/user/<int:user_id>/favorites', methods=['POST', "GET"])
@jwt_required()
def get_favs(user_id):
    if request.post:
        posted_data = request.get_json()

        if planets_id in posted_data:
            planets_id = posted_data("planet_id")

        if people_id in posted_data:
            people_id = posted_data("people_id")

        if starships_id in posted_data:
            starships_id = posted_data("starships_id")

    all_favs = list(map(lambda favorite: favorite.serialize(), Favorites.query.filter_by(user_id=user_id).all()))
    if not all_favs:
        raise APIException("No favorites assigned", status_code=404)

    return jsonify(all_favs), 200

@app.route('/people', methods=['GET'])
def get_people():
    people_query = People.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(results=all_people), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = People.query.get(people_id)
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets_query = Planets.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(results=all_planets), 200

@app.route('/planets/<int:planets_id>', methods=['GET'])
def get_planet(planets_id):
    planet = Planets.query.get(planets_id)
    return jsonify(planet.serialize()), 200

@app.route('/starships', methods=['GET'])
def get_starships():
    starships_query = Starships.query.all()
    all_starships = list(map(lambda x: x.serialize(), starships_query))
    return jsonify(results=all_starships), 200

@app.route('/starships/<int:starships_id>', methods=['GET'])
def get_starship(starships_id):
    starship = Starships.query.get(starships_id)
    return jsonify(starship.serialize()), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
