from functools import wraps, lru_cache
from flask import request, redirect, url_for, session, flash
from flask_jwt_extended import create_access_token, get_jwt_identity
from storage import db

# ---------- Authentication functions ----------

def login_user(username, password):
    """Authenticate a user and create a session"""
    user = db.get_user_by_username(username)
    if user and user.check_password(password):
        # Create JWT token with user details
        identity = {
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'agent_id': user.agent_id
        }
        access_token = create_access_token(identity=identity)
        
        # Store user info in session
        session.update({
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'agent_id': user.agent_id,
            'token': access_token
        })
        
        return True, access_token
    return False, None

def logout_user():
    """Clear user session"""
    session.clear()
    return True

# ---------- Authorization decorators ----------

def login_required(f):
    """Decorator to ensure a user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Effettua il login per accedere a questa pagina', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to ensure a user has admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Effettua il login per accedere a questa pagina', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Non hai i permessi per accedere a questa pagina', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def agent_required(f):
    """Decorator to ensure a user has agent or admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Effettua il login per accedere a questa pagina', 'warning')
            return redirect(url_for('login'))
        if session.get('role') not in ['admin', 'agent']:
            flash('Non hai i permessi per accedere a questa pagina', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------- Permission check functions ----------

def get_user_role():
    """Get current user role from session"""
    return session.get('role')

def is_admin():
    """Check if current user is admin"""
    return get_user_role() == 'admin'

def is_agent():
    """Check if current user is agent"""
    return get_user_role() == 'agent'

def is_collaborator():
    """Check if current user is collaborator"""
    return get_user_role() == 'collaborator'

@lru_cache(maxsize=128)
def can_view_customer(customer_id):
    """Check if current user can view a customer"""
    # Admins can view all customers
    if is_admin():
        return True
    
    # Retrieve customer data
    customer = db.get_customer_by_id(customer_id)
    if not customer:
        return False
    
    # Agents can view their customers
    if is_agent() and customer.agent_id == session.get('user_id'):
        return True
    
    # Collaborators can view customers of their agent
    if is_collaborator() and customer.agent_id == session.get('agent_id'):
        return True
    
    return False

@lru_cache(maxsize=128)
def can_view_order(order_id):
    """Check if current user can view an order"""
    # Admins can view all orders
    if is_admin():
        return True
    
    # Retrieve order data
    order = db.get_order_by_id(order_id)
    if not order:
        return False
    
    # Users who created the order can view it
    if order.user_id == session.get('user_id'):
        return True
    
    # Retrieve customer data for order
    customer = db.get_customer_by_id(order.customer_id)
    if not customer:
        return False
    
    # Agents can view orders for their customers
    if is_agent() and customer.agent_id == session.get('user_id'):
        return True
    
    # Collaborators can view orders for customers of their agent
    if is_collaborator() and customer.agent_id == session.get('agent_id'):
        return True
    
    return False
