"""
Routes package for the Donation Platform.
Contains all route blueprints and handlers.
"""

from .auth import auth_bp
from .main import main_bp
from .organisation import org_bp
from .campaign import campaign_bp
from .donation import donation_bp
from .user_dashboard import user_dashboard_bp
from .org_dashboard import org_dashboard_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'main_bp',
    'org_bp',
    'campaign_bp',
    'donation_bp',
    'user_dashboard_bp',
    'org_dashboard_bp',
    'admin_bp'
]
