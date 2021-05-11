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

@app.route('/user', methods=['GET'])
def get_users():
    user_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), user_query))
    return jsonify(results=all_users), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    return jsonify(user.serialize()), 200

@app.route("/user/<int:user_id>", methods=["DELETE"])
def del_user(user_id):
    sel_user = User.query.get(user_id)
    if sel_user is None:
        raise APIException("User not found", status_code=404)
    db.session.delete(sel_user)
    db.session.commit()

    return jsonify("ok"), 200

@app.route('/favorites', methods=['GET'])
def get_favorites():
    favorites_query = Favorites.query.all()
    all_favorites = list(map(lambda x: x.serialize(), favorites_query))
    return jsonify(results=all_favorites), 200

@app.route('/favorites/<int:favorites_id>', methods=['GET'])
def get_fav(favorites_id):
    favorite = Favorites.query.get(favorites_id)
    return jsonify(favorite.serialize()), 200

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
