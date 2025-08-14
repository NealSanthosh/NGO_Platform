import requests
import json
from flask import current_app
from datetime import datetime

def send_webhook(event_type, data):
    """
    Send webhook to n8n for processing
    
    Args:
        event_type (str): Type of event (e.g., 'user_registration', 'donation_completed')
        data (dict): Event data to send
    
    Returns:
        bool: True if webhook sent successfully, False otherwise
    """
    try:
        webhook_url = current_app.config.get('N8N_WEBHOOK_URL')
        if not webhook_url:
            current_app.logger.warning("N8N_WEBHOOK_URL not configured")
            return False
        
        payload = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DonationPlatform/1.0'
        }
        
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            current_app.logger.info(f"Webhook sent successfully for event: {event_type}")
            return True
        else:
            current_app.logger.error(f"Webhook failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Webhook request failed: {str(e)}")
        return False
    except Exception as e:
        current_app.logger.error(f"Webhook error: {str(e)}")
        return False

# Webhook event formats for n8n integration:

def send_user_registration_webhook(user_data):
    """
    Format: {
        "event_type": "user_registration",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "user_id": "507f1f77bcf86cd799439011",
            "email": "user@example.com",
            "username": "johndoe",
            "user_type": "donor",
            "registration_time": "2024-01-15T10:30:00Z"
        }
    }
    """
    return send_webhook('user_registration', user_data)

def send_donation_completed_webhook(donation_data):
    """
    Format: {
        "event_type": "donation_completed",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "donation_id": "507f1f77bcf86cd799439011",
            "donor_id": "507f1f77bcf86cd799439012",
            "organisation_id": "507f1f77bcf86cd799439013",
            "campaign_id": "507f1f77bcf86cd799439014",
            "amount": 100.00,
            "receipt_id": "RCP202401151030123456",
            "transaction_id": "TXN123456789",
            "is_anonymous": false
        }
    }
    """
    return send_webhook('donation_completed', donation_data)

def send_monthly_report_webhook(report_data):
    """
    Format: {
        "event_type": "monthly_report",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "report_type": "donor" | "organisation",
            "recipient_id": "507f1f77bcf86cd799439011",
            "recipient_email": "user@example.com",
            "report_period": "2024-01",
            "summary": {
                "total_donations": 500.00,
                "donation_count": 5,
                "top_campaigns": [...]
            }
        }
    }
    """
    return send_webhook('monthly_report', report_data)

def send_otp_webhook(otp_data):
    """
    Format: {
        "event_type": "send_otp",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "user_id": "507f1f77bcf86cd799439011",
            "email": "user@example.com",
            "phone": "+1234567890",
            "otp_code": "123456",
            "purpose": "email_verification" | "password_reset" | "login_verification",
            "expires_at": "2024-01-15T10:35:00Z"
        }
    }
    """
    return send_webhook('send_otp', otp_data)

def send_newsletter_webhook(newsletter_data):
    """
    Format: {
        "event_type": "newsletter_subscription",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "email": "user@example.com",
            "user_id": "507f1f77bcf86cd799439011",
            "subscription_type": "subscribe" | "unsubscribe",
            "preferences": {
                "campaigns": true,
                "organisations": true,
                "monthly_reports": true
            }
        }
    }
    """
    return send_webhook('newsletter_subscription', newsletter_data)

def send_campaign_milestone_webhook(milestone_data):
    """
    Format: {
        "event_type": "campaign_milestone",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "campaign_id": "507f1f77bcf86cd799439011",
            "organisation_id": "507f1f77bcf86cd799439012",
            "milestone_type": "50_percent" | "75_percent" | "goal_reached" | "deadline_approaching",
            "current_amount": 5000.00,
            "goal_amount": 10000.00,
            "percentage": 50.0,
            "days_remaining": 15
        }
    }
    """
    return send_webhook('campaign_milestone', milestone_data)

def send_organisation_verification_webhook(verification_data):
    """
    Format: {
        "event_type": "organisation_verification",
        "timestamp": "2024-01-15T10:30:00Z",
        "data": {
            "organisation_id": "507f1f77bcf86cd799439011",
            "organisation_name": "Example Charity",
            "user_id": "507f1f77bcf86cd799439012",
            "user_email": "admin@examplecharity.org",
            "verification_status": "pending" | "approved" | "rejected",
            "admin_notes": "Additional verification required"
        }
    }
    """
    return send_webhook('organisation_verification', verification_data)
