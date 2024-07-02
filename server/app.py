#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/activities', methods = ['GET'])
def all_activities():
    return [a.to_dict(rules=['-signups']) for a in Activity.query], 200 # iterating just query instead of iterating query.all saves memory, hence more efficient

@app.route('/activities/<int:id>', methods=['DELETE'])
def activity_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if not activity:
        return {'error': 'Activity not found'}, 404 # 404: Not Found Status Code
    db.session.delete(activity)
    db.session.commit()
    return {}, 204 # 204: No Content Status Code

@app.route('/campers', methods = ['GET', 'POST'])
def all_campers():
    if request.method == "GET":
        campers = Camper.query.all()
        return [c.to_dict(rules=['-signups']) for c in campers], 200
    elif request.method == "POST":
        data = request.get_json()
        try:
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            
        except ValueError as e:
            return {'error': 'validation failed'}, 400
        db.session.add(new_camper)
        db.session.commit()
        return new_camper.to_dict(rules = ['-signups']), 200

@app.route('/campers/<int:id>', methods = ['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if not camper:
        return {
            "error": 'Camper not found'
        }, 404
    if request.method == 'GET':
        return camper.to_dict(), 200
    elif request.method == 'PATCH':
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data: 
                camper.age = data['age']
        except ValueError as e:
            return {"errors": ["validation errors"]}, 400
        db.session.add(camper)
        db.session.commit()
        return camper.to_dict(rules = ['-signups']), 200

@app.route('/signups', methods = ['POST'])
def all_signups():
    
    data = request.get_json()
    
    try:
        new_signup = Signup(
            camper_id = data.get('camper_id'),
            activity_id = data.get('activity_id'),
            time = data.get('time')
        )
    except ValueError:
        return {'error': 'validation failed'}, 400
    
    db.session.add(new_signup)
    db.session.commit()
    
    return new_signup.to_dict(), 200
    

if __name__ == '__main__':
    app.run(port=5555, debug=True)
