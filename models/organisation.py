from bson.objectid import ObjectId
from extensions import mongo
from datetime import datetime

class Organisation:
    def __init__(self, name, description, mission, user_id, **kwargs):
        self.name = name
        self.description = description
        self.mission = mission
        self.user_id = ObjectId(user_id)
        self.created_at = datetime.utcnow()
        self.is_verified = False
        self.total_donations = 0.0
        self.logo_image = kwargs.get('logo_image')
        self.banner_image = kwargs.get('banner_image')
        self.website = kwargs.get('website')
        self.phone = kwargs.get('phone')
        self.address = kwargs.get('address')
        self.registration_number = kwargs.get('registration_number')
    
    def save(self):
        org_data = {
            'name': self.name,
            'description': self.description,
            'mission': self.mission,
            'user_id': self.user_id,
            'created_at': self.created_at,
            'is_verified': self.is_verified,
            'total_donations': self.total_donations,
            'logo_image': self.logo_image,
            'banner_image': self.banner_image,
            'website': self.website,
            'phone': self.phone,
            'address': self.address,
            'registration_number': self.registration_number
        }
        result = mongo.db.organisations.insert_one(org_data)
        self._id = result.inserted_id
        return self
    
    @staticmethod
    def get_by_id(org_id):
        try:
            org_data = mongo.db.organisations.find_one({'_id': ObjectId(org_id)})
            if org_data:
                org = Organisation.__new__(Organisation)
                org.__dict__.update(org_data)
                return org
        except:
            pass
        return None
    
    @staticmethod
    def get_by_user_id(user_id):
        org_data = mongo.db.organisations.find_one({'user_id': ObjectId(user_id)})
        if org_data:
            org = Organisation.__new__(Organisation)
            org.__dict__.update(org_data)
            return org
        return None
    
    @staticmethod
    def get_all():
        orgs = []
        for org_data in mongo.db.organisations.find({'is_verified': True}):
            org = Organisation.__new__(Organisation)
            org.__dict__.update(org_data)
            orgs.append(org)
        return orgs
    
    def update(self, **kwargs):
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            mongo.db.organisations.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        return self
    
    def get_campaigns(self):
        from models.campaign import Campaign
        return Campaign.get_by_organisation_id(str(self._id))
