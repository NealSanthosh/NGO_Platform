from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
import re
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def organisation_required(f):
    """Decorator to require organisation access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.user_type != 'organisation':
            flash('Organisation access required', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^[\+]?[\d\s\-\(\)]+$'
    return re.match(pattern, phone) is not None and len(re.sub(r'[\s\-\(\)]', '', phone)) >= 10

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date(date_obj, format_str='%B %d, %Y'):
    """Format date object to string"""
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    return str(date_obj)

def calculate_days_ago(date_obj):
    """Calculate how many days ago a date was"""
    if isinstance(date_obj, datetime):
        delta = datetime.utcnow() - date_obj
        return delta.days
    return 0

def resize_image(image_data, max_width=800, max_height=600, quality=85):
    """Resize image while maintaining aspect ratio"""
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        
        # Calculate new dimensions
        image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save as JPEG with specified quality
        output = BytesIO()
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        image.save(output, format='JPEG', quality=quality)
        
        # Return base64 encoded resized image
        return base64.b64encode(output.getvalue()).decode('utf-8')
    except Exception as e:
        return image_data  # Return original if resize fails

def generate_receipt_id():
    """Generate unique receipt ID"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    import uuid
    unique_id = str(uuid.uuid4())[-6:]
    return f"RCP{timestamp}{unique_id.upper()}"

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    safe_chars = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    return safe_chars[:100]  # Limit length

def calculate_progress_percentage(current, goal):
    """Calculate progress percentage"""
    if goal <= 0:
        return 0
    return min((current / goal) * 100, 100)

def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_large_number(number):
    """Format large numbers with K, M, B suffixes"""
    if number >= 1000000000:
        return f"{number / 1000000000:.1f}B"
    elif number >= 1000000:
        return f"{number / 1000000:.1f}M"
    elif number >= 1000:
        return f"{number / 1000:.1f}K"
    else:
        return str(int(number))

class Pagination:
    """Simple pagination helper"""
    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count
    
    @property
    def items(self):
        return self.total_count
    
    @property
    def prev_num(self):
        return self.page - 1 if self.has_prev else None
    
    @property
    def next_num(self):
        return self.page + 1 if self.has_next else None
    
    @property
    def has_prev(self):
        return self.page > 1
    
    @property
    def has_next(self):
        return self.page < self.pages
    
    @property
    def pages(self):
        return (self.total_count - 1) // self.per_page + 1
    
    def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
        last = self.pages
        for num in range(1, last + 1):
            if num <= left_edge or \
               (self.page - left_current - 1 < num < self.page + right_current) or \
               num > last - right_edge:
                yield num
