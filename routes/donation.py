from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models.donation import Donation
from models.campaign import Campaign
from models.organisation import Organisation
from utils.webhook import send_webhook
import uuid

donation_bp = Blueprint('donation', __name__)

@donation_bp.route('/<campaign_id>', methods=['GET', 'POST'])
@login_required
def donate(campaign_id):
    campaign = Campaign.get_by_id(campaign_id)
    if not campaign:
        flash('Campaign not found', 'danger')
        return redirect(url_for('campaign.list'))
    
    organisation = campaign.get_organisation()
    
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        is_anonymous = request.form.get('is_anonymous') == 'on'
        message = request.form.get('message', '')
        
        if amount <= 0:
            flash('Please enter a valid donation amount', 'danger')
            return render_template('donation/payment.html', 
                                 campaign=campaign, 
                                 organisation=organisation)
        
        # Create donation record
        donation = Donation(
            amount=amount,
            donor_id=current_user.get_id(),
            campaign_id=campaign_id,
            organisation_id=str(campaign.organisation_id),
            is_anonymous=is_anonymous,
            message=message,
            transaction_id=f"TXN{uuid.uuid4().hex[:12].upper()}"
        ).save()
        
        # Store donation ID in session for payment processing
        session['pending_donation_id'] = str(donation._id)
        
        return redirect(url_for('donation.payment', donation_id=donation._id))
    
    return render_template('donation/payment.html', 
                         campaign=campaign, 
                         organisation=organisation)

@donation_bp.route('/payment/<donation_id>')
@login_required
def payment(donation_id):
    donation = Donation.get_by_id(donation_id)
    if not donation or str(donation.donor_id) != current_user.get_id():
        flash('Donation not found', 'danger')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.get_by_id(str(donation.campaign_id))
    organisation = Organisation.get_by_id(str(donation.organisation_id))
    
    return render_template('donation/payment.html', 
                         donation=donation,
                         campaign=campaign,
                         organisation=organisation,
                         payment_step=True)

@donation_bp.route('/process-payment/<donation_id>', methods=['POST'])
@login_required
def process_payment(donation_id):
    donation = Donation.get_by_id(donation_id)
    if not donation or str(donation.donor_id) != current_user.get_id():
        flash('Donation not found', 'danger')
        return redirect(url_for('main.index'))
    
    # Simulate payment processing (dummy payment)
    payment_method = request.form.get('payment_method')
    
    # Update donation status to completed
    donation.update_status('completed')
    
    # Send webhook for completed donation
    campaign = Campaign.get_by_id(str(donation.campaign_id))
    organisation = Organisation.get_by_id(str(donation.organisation_id))
    
    send_webhook('donation_completed', {
        'donation_id': str(donation._id),
        'donor_id': current_user.get_id(),
        'organisation_id': str(donation.organisation_id),
        'campaign_id': str(donation.campaign_id),
        'amount': donation.amount,
        'receipt_id': donation.receipt_id,
        'transaction_id': donation.transaction_id,
        'is_anonymous': donation.is_anonymous,
        'donor_email': current_user.email if not donation.is_anonymous else None,
        'organisation_name': organisation.name,
        'campaign_title': campaign.title if campaign else None
    })
    
    flash('Thank you for your donation! Your payment has been processed successfully.', 'success')
    return redirect(url_for('donation.receipt', donation_id=donation._id))

@donation_bp.route('/receipt/<donation_id>')
@login_required
def receipt(donation_id):
    donation = Donation.get_by_id(donation_id)
    if not donation or str(donation.donor_id) != current_user.get_id():
        flash('Receipt not found', 'danger')
        return redirect(url_for('main.index'))
    
    campaign = Campaign.get_by_id(str(donation.campaign_id)) if donation.campaign_id else None
    organisation = Organisation.get_by_id(str(donation.organisation_id))
    
    return render_template('donation/receipt.html', 
                         donation=donation,
                         campaign=campaign,
                         organisation=organisation)
