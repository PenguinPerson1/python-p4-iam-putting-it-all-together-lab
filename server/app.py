#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            json = request.get_json()
            user = User(
                username=json['username'],
                image_url=json.get('image_url'),
                bio=json.get('bio'),
            )
            user.password_hash = json['password']
            db.session.add(user)
            db.session.commit()
            return user.to_dict(), 201
        except:
            return {}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        
        return {}, 401

class Login(Resource):
    def post(self):
        user = User.query.filter(User.username == request.json['username']).first()
        if user == None:
            return {},401
        if user.authenticate(request.json['password']):
            session['user_id'] = user.id
            return user.to_dict(),200
        return {},401

class Logout(Resource):
    def delete(self):
        if session.get('user_id')==None:
            return {}, 401
        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id') == None:
            return {}, 401
        return [recipe.to_dict() for recipe in Recipe.query.all() if recipe.user_id == session['user_id']], 200
    
    def post(self):
        try:
            recipe = Recipe( 
                title=request.json.get('title'),
                instructions = request.json.get('instructions'),
                minutes_to_complete = request.json.get('minutes_to_complete'),
                user_id = session['user_id'] )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except:
            return {},422

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)