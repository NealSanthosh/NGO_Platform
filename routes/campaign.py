from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.campaign import Campaign
from models.organisation import Organisation
from utils.webhook import send_webhook
from datetime import datetime

campaign_bp = Blueprint('campaign', __name__)

@campaign_bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    category = request.args.get('category', 'all')
    
    # Get all active campaigns
    campaigns = Campaign.get_all_active()
    
    # Filter by category if specified
    if category != 'all':
        campaigns = [c for c in campaigns if c.category.lower() == category.lower()]
    
    # Simple pagination simulation
    start = (page - 1) * per_page
    end = start + per_page
    paginated_campaigns = campaigns[start:end]
    has_next = len(campaigns) > end
    
    return render_template('campaigns/list.html', 
                         campaigns=paginated_campaigns,
                         has_next=has_next,
                         page=page,
                         current_category=category)

@campaign_bp.route('/<id>')
def detail(id):
    campaign = Campaign.get_by_id(id)
    if not campaign:
        flash('Campaign not found', 'danger')
        return redirect(url_for('campaign.list'))
    
    # Get campaign's organisation
    organisation = campaign.get_organisation()
    
    return render_template('campaigns/detail.html', 
                         campaign=campaign,
                         organisation=organisation)

@campaign_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.user_type != 'organisation':
        flash('Access denied. Only organizations can create campaigns.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get user's organisation
    org = Organisation.get_by_user_id(current_user.get_id())
    if not org:
        flash('Please create your organization profile first.', 'warning')
        return redirect(url_for('org.create'))
    
    if not org.is_verified:
        flash('Your organization must be verified before creating campaigns.', 'warning')
        return redirect(url_for('org_dashboard.dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        goal_amount = float(request.form.get('goal_amount', 0))
        category = request.form.get('category', 'General')
        end_date_str = request.form.get('end_date')
        
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Create new campaign
        campaign = Campaign(
            title=title,
            description=description,
            goal_amount=goal_amount,
            organisation_id=str(org._id),
            category=category,
            end_date=end_date
        ).save()
        
        # Send webhook for campaign creation
        send_webhook('campaign_created', {
            'campaign_id': str(campaign._id),
            'title': campaign.title,
            'organisation_id': str(org._id),
            'organisation_name': org.name,
            'goal_amount': campaign.goal_amount,
            'created_at': campaign.created_at.isoformat()
        })
        
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaign.detail', id=campaign._id))
    
    return render_template('campaigns/create.html', organisation=org)
