from bson.objectid import ObjectId
from extensions import mongo
from datetime import datetime

class Campaign:
    def __init__(self, title, description, goal_amount, organisation_id, **kwargs):
        self.title = title
        self.description = description
        self.goal_amount = float(goal_amount)
        self.raised_amount = 0.0
        self.organisation_id = ObjectId(organisation_id)
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.end_date = kwargs.get('end_date')
        self.banner_image = kwargs.get('banner_image')
        self.category = kwargs.get('category', 'General')
    
    def save(self):
        campaign_data = {
            'title': self.title,
            'description': self.description,
            'goal_amount': self.goal_amount,
            'raised_amount': self.raised_amount,
            'organisation_id': self.organisation_id,
            'created_at': self.created_at,
            'is_active': self.is_active,
            'end_date': self.end_date,
            'banner_image': self.banner_image,
            'category': self.category
        }
        result = mongo.db.campaigns.insert_one(campaign_data)
        self._id = result.inserted_id
        return self
    
    @staticmethod
    def get_by_id(campaign_id):
        try:
            campaign_data = mongo.db.campaigns.find_one({'_id': ObjectId(campaign_id)})
            if campaign_data:
                campaign = Campaign.__new__(Campaign)
                campaign.__dict__.update(campaign_data)
                return campaign
        except:
            pass
        return None
    
    @staticmethod
    def get_by_organisation_id(org_id):
        campaigns = []
        for campaign_data in mongo.db.campaigns.find({'organisation_id': ObjectId(org_id)}):
            campaign = Campaign.__new__(Campaign)
            campaign.__dict__.update(campaign_data)
            campaigns.append(campaign)
        return campaigns
    
    @staticmethod
    def get_all_active():
        campaigns = []
        for campaign_data in mongo.db.campaigns.find({'is_active': True}):
            campaign = Campaign.__new__(Campaign)
            campaign.__dict__.update(campaign_data)
            campaigns.append(campaign)
        return campaigns
    
    def update(self, **kwargs):
        update_data = {}
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
                update_data[key] = value
        
        if update_data:
            mongo.db.campaigns.update_one(
                {'_id': self._id},
                {'$set': update_data}
            )
        return self
    
    def get_organisation(self):
        from models.organisation import Organisation
        return Organisation.get_by_id(str(self.organisation_id))
    
    @property
    def progress_percentage(self):
        if self.goal_amount > 0:
            return min((self.raised_amount / self.goal_amount) * 100, 100)
        return 0
