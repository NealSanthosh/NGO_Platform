from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from models.organisation import Organisation
from utils.webhook import send_webhook

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.get_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            
            # Send login notification via webhook
            send_webhook('user_login', {
                'user_id': str(user._id),
                'email': user.email,
                'user_type': user.user_type,
                'login_time': user.created_at.isoformat()
            })
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.user_type == 'organisation':
                return redirect(url_for('org_dashboard.dashboard'))
            else:
                return redirect(url_for('user_dashboard.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('user_type', 'donor')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Check if user already exists
        if User.get_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            user_type=user_type,
            phone=phone
        ).save()
        
        # Send registration webhook
        send_webhook('user_registration', {
            'user_id': str(user._id),
            'email': user.email,
            'username': user.username,
            'user_type': user.user_type,
            'registration_time': user.created_at.isoformat()
        })
        
        login_user(user)
        
        if user_type == 'organisation':
            flash('Registration successful! Please set up your organisation profile.', 'success')
            return redirect(url_for('org_dashboard.setup_organisation'))
        else:
            flash('Registration successful!', 'success')
            return redirect(url_for('user_dashboard.dashboard'))
    
    return render_template('auth/register.html')

@auth_bp.route('/choose-type')
def choose_type():
    return render_template('auth/choose_type.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))
