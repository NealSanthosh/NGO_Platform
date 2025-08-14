from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import current_app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime

class User(UserMixin):
    def __init__(self, username, email, password, user_type='donor', **kwargs):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.profile_image = kwargs.get('profile_image')
        self.phone = kwargs.get('phone')
        self.address = kwargs.get('address')
        
    def get_id(self):
        return str(self._id)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def save(self):
        mongo = PyMongo(current_app)
        user_data = {
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'user_type': self.user_type,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'profile_image': self.profile_image,
            'phone': self.phone,
            'address': self.address
        }
        result = mongo.db.users.insert_one(user_data)
        self._id = result.inserted_id
        return self
    
    @staticmethod
    def get_by_id(user_id):
        try:
            mongo = PyMongo(current_app)
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_data:
                user = User.__new__(User)
                user.__dict__.update(user_data)
                return user
        except:
            pass
        return None
    
    @staticmethod
    def get_by_email(email):
        mongo = PyMongo(current_app)
        user_data = mongo.db.users.find_one({'email': email})
        if user_data:
            user = User.__new__(User)
            user.__dict__.update(user_data)
            return user
        return None
    
    def update(self, **kwargs):
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            mongo.db.users.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        return self
