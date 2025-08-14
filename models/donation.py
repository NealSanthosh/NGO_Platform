from bson.objectid import ObjectId
from extensions import mongo
from datetime import datetime

class Donation:
    def __init__(self, amount, donor_id, campaign_id, organisation_id, **kwargs):
        self.amount = float(amount)
        self.donor_id = ObjectId(donor_id)
        self.campaign_id = ObjectId(campaign_id) if campaign_id else None
        self.organisation_id = ObjectId(organisation_id)
        self.created_at = datetime.utcnow()
        self.payment_status = 'pending'  # pending, completed, failed, refunded
        self.transaction_id = kwargs.get('transaction_id')
        self.is_anonymous = kwargs.get('is_anonymous', False)
        self.message = kwargs.get('message', '')
        self.receipt_id = f"RCP{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{str(ObjectId())[-6:]}"
    
    def save(self):
        donation_data = {
            'amount': self.amount,
            'donor_id': self.donor_id,
            'campaign_id': self.campaign_id,
            'organisation_id': self.organisation_id,
            'created_at': self.created_at,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'is_anonymous': self.is_anonymous,
            'message': self.message,
            'receipt_id': self.receipt_id
        }
        result = mongo.db.donations.insert_one(donation_data)
        self._id = result.inserted_id
        return self
    
    @staticmethod
    def get_by_id(donation_id):
        try:
            donation_data = mongo.db.donations.find_one({'_id': ObjectId(donation_id)})
            if donation_data:
                donation = Donation.__new__(Donation)
                donation.__dict__.update(donation_data)
                return donation
        except:
            pass
        return None
    
    @staticmethod
    def get_by_donor_id(donor_id):
        donations = []
        for donation_data in mongo.db.donations.find({'donor_id': ObjectId(donor_id)}):
            donation = Donation.__new__(Donation)
            donation.__dict__.update(donation_data)
            donations.append(donation)
        return donations
    
    @staticmethod
    def get_by_organisation_id(org_id):
        donations = []
        for donation_data in mongo.db.donations.find({'organisation_id': ObjectId(org_id)}):
            donation = Donation.__new__(Donation)
            donation.__dict__.update(donation_data)
            donations.append(donation)
        return donations
    
    def update_status(self, status):
        self.payment_status = status
        mongo.db.donations.update_one(
            {'_id': self._id},
            {'$set': {'payment_status': status}}
        )
        
        # Update campaign raised amount if payment is completed
        if status == 'completed' and self.campaign_id:
            mongo.db.campaigns.update_one(
                {'_id': self.campaign_id},
                {'$inc': {'raised_amount': self.amount}}
            )
            
        # Update organisation total donations
        if status == 'completed':
            mongo.db.organisations.update_one(
                {'_id': self.organisation_id},
                {'$inc': {'total_donations': self.amount}}
            )
        
        return self
