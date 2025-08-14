from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.organisation import Organisation
from models.campaign import Campaign
from models.donation import Donation
from utils.webhook import send_webhook

org_dashboard_bp = Blueprint('org_dashboard', __name__)

@org_dashboard_bp.route('/')
@login_required
def dashboard():
    if current_user.user_type != 'organisation':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get user's organisation
    org = Organisation.get_by_user_id(current_user.get_id())
    if not org:
        flash('Please set up your organisation profile first.', 'warning')
        return redirect(url_for('org_dashboard.setup_organisation'))
    
    # Get organisation statistics
    campaigns = org.get_campaigns()
    donations = Donation.get_by_organisation_id(str(org._id))
    completed_donations = [d for d in donations if d.payment_status == 'completed']
    
    total_raised = sum(d.amount for d in completed_donations)
    donation_count = len(completed_donations)
    campaign_count = len(campaigns)
    active_campaigns = len([c for c in campaigns if c.is_active])
    
    # Recent donations (last 10)
    recent_donations = sorted(completed_donations, key=lambda x: x.created_at, reverse=True)[:10]
    
    return render_template('dashboards/organisation.html',
                         organisation=org,
                         campaigns=campaigns,
                         total_raised=total_raised,
                         donation_count=donation_count,
                         campaign_count=campaign_count,
                         active_campaigns=active_campaigns,
                         recent_donations=recent_donations)

@org_dashboard_bp.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_organisation():
    if current_user.user_type != 'organisation':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if organisation already exists
    existing_org = Organisation.get_by_user_id(current_user.get_id())
    if existing_org:
        return redirect(url_for('org_dashboard.dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        mission = request.form.get('mission')
        website = request.form.get('website')
        phone = request.form.get('phone')
        address = request.form.get('address')
        registration_number = request.form.get('registration_number')
        
        # Handle image uploads
        logo_image_url = None
        banner_image_url = None
        
        logo_image = request.files.get('logo_image')
        if logo_image and logo_image.filename:
            from models.image import Image
            image = Image.create_from_file(
                logo_image,
                current_user.get_id(),
                category='organisation_logo',
                alt_text=f"{name} logo"
            )
            if image:
                logo_image_url = image.get_data_url()
        
        banner_image = request.files.get('banner_image')
        if banner_image and banner_image.filename:
            from models.image import Image
            image = Image.create_from_file(
                banner_image,
                current_user.get_id(),
                category='organisation_banner',
                alt_text=f"{name} banner"
            )
            if image:
                banner_image_url = image.get_data_url()
        
        # Create organisation
        org = Organisation(
            name=name,
            description=description,
            mission=mission,
            user_id=current_user.get_id(),
            website=website,
            phone=phone,
            address=address,
            registration_number=registration_number,
            logo_image=logo_image_url,
            banner_image=banner_image_url
        ).save()
        
        # Send webhook for verification request
        send_webhook('organisation_verification', {
            'organisation_id': str(org._id),
            'organisation_name': org.name,
            'user_id': current_user.get_id(),
            'user_email': current_user.email,
            'verification_status': 'pending',
            'registration_number': org.registration_number
        })
        
        flash('Organisation profile created! Awaiting admin verification.', 'success')
        return redirect(url_for('org_dashboard.dashboard'))
    
    return render_template('dashboards/org_setup.html')

@org_dashboard_bp.route('/campaigns')
@login_required
def campaigns():
    if current_user.user_type != 'organisation':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    org = Organisation.get_by_user_id(current_user.get_id())
    if not org:
        flash('Please set up your organisation profile first.', 'warning')
        return redirect(url_for('org_dashboard.setup_organisation'))
    
    campaigns = org.get_campaigns()
    
    return render_template('dashboards/org_campaigns.html',
                         organisation=org,
                         campaigns=campaigns)

@org_dashboard_bp.route('/donations')
@login_required
def donations():
    if current_user.user_type != 'organisation':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    org = Organisation.get_by_user_id(current_user.get_id())
    if not org:
        return redirect(url_for('org_dashboard.setup_organisation'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    donations = Donation.get_by_organisation_id(str(org._id))
    donations = sorted(donations, key=lambda x: x.created_at, reverse=True)
    
    # Simple pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_donations = donations[start:end]
    has_next = len(donations) > end
    
    # Get additional details for each donation
    donation_details = []
    for donation in paginated_donations:
        campaign = Campaign.get_by_id(str(donation.campaign_id)) if donation.campaign_id else None
        donation_details.append({
            'donation': donation,
            'campaign': campaign
        })
    
    return render_template('dashboards/org_donations.html',
                         organisation=org,
                         donation_details=donation_details,
                         has_next=has_next,
                         page=page)
