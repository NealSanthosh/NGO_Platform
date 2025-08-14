# routes/main.py
from flask import Blueprint, render_template
from extensions import mongo  # Import from extensions, NOT from app
from models.organisation import Organisation
from models.campaign import Campaign
from flask_pymongo import PyMongo

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Get statistics - this should now work
    org_count = mongo.db.organisations.count_documents({'is_verified': True})
    campaign_count = mongo.db.campaigns.count_documents({'is_active': True})
    total_donations = mongo.db.donations.aggregate([
        {'$match': {'payment_status': 'completed'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
    ])
    total_raised = list(total_donations)
    total_raised = total_raised[0]['total'] if total_raised else 0
    
    # Get featured campaigns and organisations
    featured_campaigns = Campaign.get_all_active()[:6]
    featured_orgs = Organisation.get_all()[:6]
    
    return render_template('index.html', 
                         org_count=org_count,
                         campaign_count=campaign_count,
                         total_raised=total_raised,
                         featured_campaigns=featured_campaigns,
                         featured_orgs=featured_orgs)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/test-db')
def test_db():
    """Test database connection"""
    mongo = PyMongo(app)
    try:
        collections = mongo.db.list_collection_names()
        return f"✅ Database connected! Collections: {collections}"
    except Exception as e:
        return f"❌ Database error: {str(e)}"