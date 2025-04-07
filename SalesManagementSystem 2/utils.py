from datetime import datetime
from functools import lru_cache
from flask import session
from storage import db

# ---------- Formatting functions ----------

def format_currency(value):
    """Format a numeric value as currency with Euro symbol"""
    try:
        return f"€{float(value):,.2f}"
    except (ValueError, TypeError):
        return "€0.00"

def format_date(date_obj):
    """Format a date object as a string in Italian format (DD/MM/YYYY)"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%d/%m/%Y")
    
    return ""

# ---------- Order calculation functions ----------

@lru_cache(maxsize=128)
def get_order_total(order_id):
    """Calculate the total amount for an order with caching for performance"""
    items = db.get_items_by_order(order_id)
    return sum(item.total for item in items)

@lru_cache(maxsize=128)
def get_order_paid_amount(order_id):
    """Calculate the total paid amount for an order with caching for performance"""
    payments = db.get_payments_by_order(order_id)
    return sum(payment.amount for payment in payments)

def get_order_balance(order_id):
    """Calculate the remaining balance for an order"""
    return get_order_total(order_id) - get_order_paid_amount(order_id)

# ---------- Data retrieval functions with enrichment ----------

def get_order_items_with_details(order_id):
    """Get order items with product details"""
    items = db.get_items_by_order(order_id)
    result = []
    
    # Get all products at once to avoid multiple database calls
    product_ids = [item.product_id for item in items]
    products = {p.id: p for p in [db.get_product_by_id(pid) for pid in set(product_ids)] if p}
    
    for item in items:
        product = products.get(item.product_id)
        if product:
            item_dict = item.to_dict()
            item_dict.update({
                'product_name': product.name,
                'product_code': product.code,
                'total': item.total,
                'commission_amount': item.commission_amount
            })
            result.append(item_dict)
    
    return result

def get_order_with_details(order_id):
    """Get an order with customer and items details"""
    order = db.get_order_by_id(order_id)
    if not order:
        return None
    
    # Get related entities in parallel
    customer = db.get_customer_by_id(order.customer_id)
    user = db.get_user_by_id(order.user_id)
    
    # Create enriched order dictionary
    order_dict = order.to_dict()
    order_dict.update({
        'customer_name': customer.name if customer else "Unknown",
        'created_by': user.username if user else "Unknown",
        'total_amount': get_order_total(order.id),
        'paid_amount': get_order_paid_amount(order.id),
        'balance': get_order_balance(order.id),
        'order_items': get_order_items_with_details(order.id)
    })
    
    return order_dict

def get_customer_orders(customer_id):
    """Get all orders for a customer with details"""
    orders = db.get_orders_by_customer(customer_id)
    
    # Process all orders in a more efficient way
    result = []
    for order in orders:
        order_dict = order.to_dict()
        order_dict.update({
            'total_amount': get_order_total(order.id),
            'paid_amount': get_order_paid_amount(order.id),
            'balance': get_order_balance(order.id)
        })
        result.append(order_dict)
    
    return result

# ---------- Business logic functions ----------

def calculate_commission(user_id, start_date=None, end_date=None):
    """Calculate commission for a user in a date range"""
    # Set default date range if not provided
    if start_date is None:
        start_date = datetime(datetime.now().year, datetime.now().month, 1)
    if end_date is None:
        end_date = datetime.now()
    
    # Get orders based on user role
    role = session.get('role')
    if role == 'admin':
        orders = db.get_all_orders()
    elif role == 'agent':
        orders = db.get_orders_by_agent(user_id)
    else:
        orders = db.get_orders_by_user(user_id)
    
    # Filter orders by date range and calculate totals
    total_commission = 0.0
    total_sales = 0.0
    
    for order in orders:
        if (start_date and order.order_date < start_date) or (end_date and order.order_date > end_date):
            continue
        
        items = db.get_items_by_order(order.id)
        for item in items:
            item_total = item.total
            total_sales += item_total
            total_commission += item.commission_amount
    
    return {
        'total_sales': total_sales,
        'total_commission': total_commission,
        'start_date': start_date,
        'end_date': end_date
    }
