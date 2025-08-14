from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.donation import Donation
from models.campaign import Campaign
from models.organisation import Organisation
from extensions import mongo
from datetime import datetime, timedelta

user_dashboard_bp = Blueprint('user_dashboard', __name__)

@user_dashboard_bp.route('/')
@login_required
def dashboard():
    if current_user.user_type != 'donor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    # Get user's donation statistics
    user_donations = Donation.get_by_donor_id(current_user.get_id())
    completed_donations = [d for d in user_donations if d.payment_status == 'completed']
    
    total_donated = sum(d.amount for d in completed_donations)
    donation_count = len(completed_donations)
    
    # Get recent donations (last 5)
    recent_donations = sorted(completed_donations, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Get supported campaigns and organisations
    campaign_ids = list(set(str(d.campaign_id) for d in completed_donations if d.campaign_id))
    org_ids = list(set(str(d.organisation_id) for d in completed_donations))
    
    supported_campaigns = []
    for campaign_id in campaign_ids:
        campaign = Campaign.get_by_id(campaign_id)
        if campaign:
            supported_campaigns.append(campaign)
    
    supported_orgs = []
    for org_id in org_ids:
        org = Organisation.get_by_id(org_id)
        if org:
            supported_orgs.append(org)
    
    return render_template('dashboards/user.html',
                         total_donated=total_donated,
                         donation_count=donation_count,
                         recent_donations=recent_donations,
                         supported_campaigns=supported_campaigns,
                         supported_orgs=supported_orgs)

@user_dashboard_bp.route('/donations')
@login_required
def donations():
    if current_user.user_type != 'donor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    user_donations = Donation.get_by_donor_id(current_user.get_id())
    user_donations = sorted(user_donations, key=lambda x: x.created_at, reverse=True)
    
    # Simple pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_donations = user_donations[start:end]
    has_next = len(user_donations) > end
    
    # Get campaign and organisation details for each donation
    donation_details = []
    for donation in paginated_donations:
        campaign = Campaign.get_by_id(str(donation.campaign_id)) if donation.campaign_id else None
        organisation = Organisation.get_by_id(str(donation.organisation_id))
        donation_details.append({
            'donation': donation,
            'campaign': campaign,
            'organisation': organisation
        })
    
    return render_template('dashboards/user_donations.html',
                         donation_details=donation_details,
                         has_next=has_next,
                         page=page)

@user_dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.user_type != 'donor':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        # Handle profile image upload
        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            from models.image import Image
            image = Image.create_from_file(
                profile_image,
                current_user.get_id(),
                category='profile',
                alt_text=f"{username}'s profile picture"
            )
            if image:
                current_user.update(profile_image=image.get_data_url())
        
        current_user.update(
            username=username,
            phone=phone,
            address=address
        )
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard.profile'))
    
    return render_template('dashboards/user_profile.html')
