from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.user import User
from models.organisation import Organisation
from models.campaign import Campaign
from models.donation import Donation
from extensions import mongo
from utils.webhook import send_webhook
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def require_admin():
    if not current_user.is_authenticated or current_user.user_type != 'admin':
        flash('Admin access required', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
def dashboard():
    # Get overall statistics
    total_users = mongo.db.users.count_documents({})
    total_orgs = mongo.db.organisations.count_documents({})
    total_campaigns = mongo.db.campaigns.count_documents({})
    pending_verifications = mongo.db.organisations.count_documents({'is_verified': False})
    
    # Financial statistics
    total_donations = list(mongo.db.donations.aggregate([
        {'$match': {'payment_status': 'completed'}},
        {'$group': {'_id': None, 'total': {'$sum': '$amount'}, 'count': {'$sum': 1}}}
    ]))
    
    total_raised = total_donations[0]['total'] if total_donations else 0
    donation_count = total_donations[0]['count'] if total_donations else 0
    
    # Recent activity
    recent_donations = list(mongo.db.donations.find().sort('created_at', -1).limit(10))
    recent_orgs = list(mongo.db.organisations.find().sort('created_at', -1).limit(5))
    
    return render_template('dashboards/admin.html',
                         total_users=total_users,
                         total_orgs=total_orgs,
                         total_campaigns=total_campaigns,
                         pending_verifications=pending_verifications,
                         total_raised=total_raised,
                         donation_count=donation_count,
                         recent_donations=recent_donations,
                         recent_orgs=recent_orgs)

@admin_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = list(mongo.db.users.find().sort('created_at', -1))
    
    # Simple pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = users[start:end]
    has_next = len(users) > end
    
    return render_template('admin/users.html',
                         users=paginated_users,
                         has_next=has_next,
                         page=page)

@admin_bp.route('/organisations')
def organisations():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status = request.args.get('status', 'all')
    
    query = {}
    if status == 'verified':
        query['is_verified'] = True
    elif status == 'pending':
        query['is_verified'] = False
    
    orgs = list(mongo.db.organisations.find(query).sort('created_at', -1))
    
    # Simple pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_orgs = orgs[start:end]
    has_next = len(orgs) > end
    
    return render_template('admin/organisations.html',
                         organisations=paginated_orgs,
                         has_next=has_next,
                         page=page,
                         current_status=status)

@admin_bp.route('/verify-organisation/<org_id>', methods=['POST'])
def verify_organisation(org_id):
    org = Organisation.get_by_id(org_id)
    if not org:
        return jsonify({'success': False, 'message': 'Organisation not found'})
    
    action = request.json.get('action')  # 'approve' or 'reject'
    notes = request.json.get('notes', '')
    
    if action == 'approve':
        org.update(is_verified=True)
        flash('Organisation verified successfully', 'success')
        
        # Send approval webhook
        send_webhook('organisation_verification', {
            'organisation_id': str(org._id),
            'organisation_name': org.name,
            'user_id': str(org.user_id),
            'verification_status': 'approved',
            'admin_notes': notes,
            'verified_at': datetime.utcnow().isoformat()
        })
        
    elif action == 'reject':
        # Send rejection webhook
        send_webhook('organisation_verification', {
            'organisation_id': str(org._id),
            'organisation_name': org.name,
            'user_id': str(org.user_id),
            'verification_status': 'rejected',
            'admin_notes': notes,
            'rejected_at': datetime.utcnow().isoformat()
        })
    
    return jsonify({'success': True, 'message': f'Organisation {action}ed successfully'})

@admin_bp.route('/financial-reports')
def financial_reports():
    # Monthly donation summary
    monthly_data = list(mongo.db.donations.aggregate([
        {'$match': {'payment_status': 'completed'}},
        {'$group': {
            '_id': {
                'year': {'$year': '$created_at'},
                'month': {'$month': '$created_at'}
            },
            'total': {'$sum': '$amount'},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': -1}},
        {'$limit': 12}
    ]))
    
    # Top performing campaigns
    top_campaigns = list(mongo.db.campaigns.aggregate([
        {'$sort': {'raised_amount': -1}},
        {'$limit': 10}
    ]))
    
    # Convert to Campaign objects
    top_campaigns = [Campaign.get_by_id(str(c['_id'])) for c in top_campaigns]
    top_campaigns = [c for c in top_campaigns if c]  # Filter out None values
    
    # Top organisations by donations received
    top_orgs = list(mongo.db.organisations.aggregate([
        {'$sort': {'total_donations': -1}},
        {'$limit': 10}
    ]))
    
    # Convert to Organisation objects
    top_orgs = [Organisation.get_by_id(str(o['_id'])) for o in top_orgs]
    top_orgs = [o for o in top_orgs if o]  # Filter out None values
    
    return render_template('admin/financial_reports.html',
                         monthly_data=monthly_data,
                         top_campaigns=top_campaigns,
                         top_orgs=top_orgs)

@admin_bp.route('/database-management')
def database_management():
    # Collection statistics
    collections = {
        'users': mongo.db.users.count_documents({}),
        'organisations': mongo.db.organisations.count_documents({}),
        'campaigns': mongo.db.campaigns.count_documents({}),
        'donations': mongo.db.donations.count_documents({}),
        'images': mongo.db.images.count_documents({})
    }
    
    return render_template('admin/database.html', collections=collections)

@admin_bp.route('/api/stats')
def api_stats():
    """API endpoint for real-time dashboard stats"""
    stats = {
        'total_users': mongo.db.users.count_documents({}),
        'total_orgs': mongo.db.organisations.count_documents({}),
        'total_campaigns': mongo.db.campaigns.count_documents({}),
        'pending_verifications': mongo.db.organisations.count_documents({'is_verified': False})
    }
    return jsonify(stats)

@admin_bp.route('/export/<data_type>')
def export_data(data_type):
    """Export data in various formats"""
    format_type = request.args.get('format', 'csv')
    
    # This would implement actual data export functionality
    # For now, return a simple response
    return jsonify({
        'success': True,
        'message': f'Export of {data_type} in {format_type} format initiated',
        'download_url': f'/downloads/{data_type}_{datetime.now().strftime("%Y%m%d")}.{format_type}'
    })
