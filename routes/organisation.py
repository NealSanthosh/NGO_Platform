from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.organisation import Organisation
from models.campaign import Campaign
from models.user import User
from utils.webhook import send_webhook

org_bp = Blueprint('org', __name__)

@org_bp.route('/')
def list():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Get all verified organisations
    orgs = Organisation.get_all()
    
    # Simple pagination simulation
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orgs = orgs[start:end]
    has_next = len(orgs) > end
    
    return render_template('organisations/list.html', 
                         organisations=paginated_orgs,
                         has_next=has_next,
                         page=page)

@org_bp.route('/<id>')
def detail(id):
    org = Organisation.get_by_id(id)
    if not org:
        flash('Organization not found', 'danger')
        return redirect(url_for('org.list'))
    
    # Get organisation's campaigns
    campaigns = org.get_campaigns()
    
    return render_template('organisations/detail.html', 
                         organisation=org,
                         campaigns=campaigns)

@org_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if current_user.user_type != 'organisation':
        flash('Access denied. Only organizations can create profiles.', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if user already has an organization
    existing_org = Organisation.get_by_user_id(current_user.get_id())
    if existing_org:
        flash('You already have an organization profile.', 'info')
        return redirect(url_for('org_dashboard.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        mission = request.form.get('mission')
        website = request.form.get('website')
        phone = request.form.get('phone')
        address = request.form.get('address')
        registration_number = request.form.get('registration_number')
        
        # Create new organisation
        org = Organisation(
            name=name,
            description=description,
            mission=mission,
            user_id=current_user.get_id(),
            website=website,
            phone=phone,
            address=address,
            registration_number=registration_number
        ).save()
        
        # Send webhook for organisation creation
        send_webhook('organisation_created', {
            'organisation_id': str(org._id),
            'name': org.name,
            'user_id': current_user.get_id(),
            'user_email': current_user.email,
            'created_at': org.created_at.isoformat()
        })
        
        flash('Organisation profile created successfully! Awaiting verification.', 'success')
        return redirect(url_for('org_dashboard.dashboard'))
    
    return render_template('organisations/create.html')
