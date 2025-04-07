from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Base model class with common functionality
class BaseModel:
    def __init__(self):
        self.created_at = datetime.now()
    
    def _format_datetime(self, dt):
        return dt.isoformat() if dt else None
    
    def to_dict(self):
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = self._format_datetime(value)
            else:
                result[key] = value
        return result

# Model definitions
class User(BaseModel):
    def __init__(self, id, username, email, password, role, full_name=None, agent_id=None):
        super().__init__()
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role  # 'admin', 'agent', 'collaborator'
        self.full_name = full_name
        self.agent_id = agent_id  # For collaborators, this links to their agent
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(BaseModel):
    def __init__(self, id, name, vat_number, address, city, zip_code, country, contact_person=None, email=None, phone=None, agent_id=None):
        super().__init__()
        self.id = id
        self.name = name
        self.vat_number = vat_number
        self.address = address
        self.city = city
        self.zip_code = zip_code
        self.country = country
        self.contact_person = contact_person
        self.email = email
        self.phone = phone
        self.agent_id = agent_id  # Which agent manages this customer

class Product(BaseModel):
    def __init__(self, id, name, code, description, price, unit, category=None):
        super().__init__()
        self.id = id
        self.name = name
        self.code = code
        self.description = description
        self.price = price
        self.unit = unit
        self.category = category

class PriceList(BaseModel):
    def __init__(self, id, customer_id, product_id, custom_price):
        super().__init__()
        self.id = id
        self.customer_id = customer_id
        self.product_id = product_id
        self.custom_price = custom_price

class Order(BaseModel):
    def __init__(self, id, customer_id, order_date, user_id, status='pending', notes=None, order_code=None):
        super().__init__()
        self.id = id
        self.customer_id = customer_id
        self.order_date = order_date
        self.user_id = user_id  # Who created the order
        self.status = status  # pending, confirmed, shipped, delivered, cancelled
        self.notes = notes
        self.updated_at = datetime.now()
        
        # Generate unique order code
        if id is None:
            timestamp = datetime.now().strftime('%Y%m%d%H%M')
            self.order_code = f"ORD-{timestamp}"
        else:
            self.order_code = order_code or f"ORD-{id:06d}"

class OrderItem(BaseModel):
    def __init__(self, id, order_id, product_id, quantity, price, commission_rate=0.0):
        super().__init__()
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.commission_rate = commission_rate
    
    @property
    def total(self):
        """Calculate the total for this item"""
        return self.price * self.quantity
    
    @property
    def commission_amount(self):
        """Calculate the commission amount for this item"""
        return self.total * self.commission_rate / 100

class Payment(BaseModel):
    def __init__(self, id, order_id, amount, payment_date, payment_method, notes=None):
        super().__init__()
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.notes = notes
