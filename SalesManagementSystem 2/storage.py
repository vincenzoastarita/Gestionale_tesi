from datetime import datetime
from functools import lru_cache
from models import User, Customer, Product, PriceList, Order, OrderItem, Payment

# In-memory storage with caching for MVP
class Storage:
    def __init__(self):
        # Data stores
        self.users = {}
        self.customers = {}
        self.products = {}
        self.price_lists = {}
        self.orders = {}
        self.order_items = {}
        self.payments = {}
        
        # Cache invalidation flags for each entity type
        self._cache_invalidation_counters = {
            'users': 0,
            'customers': 0,
            'products': 0,
            'price_lists': 0,
            'orders': 0,
            'order_items': 0,
            'payments': 0
        }
        
        # Initialize demo data
        self._init_demo_data()
    
    def _get_cache_key(self, entity_type):
        """Get a cache key for a specific entity type that changes on every cache invalidation"""
        return f"{entity_type}_{self._cache_invalidation_counters[entity_type]}"
    
    def _invalidate_cache(self, entity_type):
        """Invalidate the cache for a specific entity type"""
        self._cache_invalidation_counters[entity_type] += 1

    def _init_demo_data(self):
        # Create admin user
        admin = User(
            id=1,
            username="admin",
            email="admin@example.com",
            password="admin123",
            role="admin",
            full_name="Administrator"
        )
        self.users[admin.id] = admin
        
        # Create basic customer
        basic_customer = Customer(
            id=999,
            name="Cliente Basic SRL",
            vat_number="IT12345678901",
            address="Via Roma 123",
            city="Milano",
            zip_code="20100",
            country="Italia",
            contact_person="Mario Rossi",
            email="info@clientebasic.it",
            phone="+39 02 1234567",
            agent_id=2
        )
        self.customers[basic_customer.id] = basic_customer
        
        # Create custom price for the basic customer
        basic_price = PriceList(
            id=1,
            customer_id=999,
            product_id=6,
            custom_price=89.99  # Prezzo scontato per il cliente basic
        )
        self.price_lists[basic_price.id] = basic_price

        # Create agent user
        agent = User(
            id=2,
            username="agent1",
            email="agent1@example.com",
            password="agent123",
            role="agent",
            full_name="Main Agent"
        )
        self.users[agent.id] = agent
        
        # Create collaborator user
        collaborator = User(
            id=3,
            username="collab1",
            email="collab1@example.com",
            password="collab123",
            role="collaborator",
            full_name="First Collaborator",
            agent_id=2  # Linked to agent1
        )
        self.users[collaborator.id] = collaborator
        
        # Create some products
        products = [
            Product(id=1, name="Office Chair", code="FURN-001", description="Ergonomic office chair", price=199.99, unit="piece", category="Furniture"),
            Product(id=2, name="Office Desk", code="FURN-002", description="Modern office desk", price=299.99, unit="piece", category="Furniture"),
            Product(id=3, name="Laptop", code="TECH-001", description="15.6 inch business laptop", price=999.99, unit="piece", category="Technology"),
            Product(id=4, name="Monitor", code="TECH-002", description="24 inch LED monitor", price=249.99, unit="piece", category="Technology"),
            Product(id=5, name="Printer", code="TECH-003", description="Color laser printer", price=399.99, unit="piece", category="Technology"),
            Product(id=6, name="Prodotto Basic", code="BASIC-001", description="Prodotto base per clienti standard", price=99.99, unit="pezzo", category="Base")
        ]
        
        for product in products:
            self.products[product.id] = product

    # User methods
    @lru_cache(maxsize=32)
    def get_user_by_id(self, user_id):
        """Get a user by ID with caching for better performance"""
        return self.users.get(user_id)
    
    @lru_cache(maxsize=32)
    def get_user_by_username(self, username):
        """Get a user by username with caching for better performance"""
        # Use more efficient lookup with dictionary
        username_to_user = {user.username: user for user in self.users.values()}
        return username_to_user.get(username)
    
    def add_user(self, user):
        if user.id is None:
            user.id = max(self.users.keys(), default=0) + 1
        self.users[user.id] = user
        return user
    
    def update_user(self, user):
        if user.id in self.users:
            self.users[user.id] = user
            return user
        return None
    
    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    def get_all_users(self):
        return list(self.users.values())
    
    def get_collaborators_by_agent(self, agent_id):
        return [u for u in self.users.values() if u.role == "collaborator" and u.agent_id == agent_id]
    
    # Customer methods
    @lru_cache(maxsize=64)
    def get_customer_by_id(self, customer_id):
        """Get a customer by ID with caching for better performance"""
        return self.customers.get(customer_id)
    
    def add_customer(self, customer):
        """Add a new customer with automatic ID assignment"""
        if customer.id is None:
            customer.id = max(self.customers.keys(), default=0) + 1
        self.customers[customer.id] = customer
        self._invalidate_cache('customers')
        return customer
    
    def update_customer(self, customer):
        """Update an existing customer"""
        if customer.id in self.customers:
            self.customers[customer.id] = customer
            self._invalidate_cache('customers')
            return customer
        return None
    
    def delete_customer(self, customer_id):
        """Delete a customer by ID and invalidate cache"""
        if customer_id in self.customers:
            del self.customers[customer_id]
            self._invalidate_cache('customers')
            return True
        return False
    
    @lru_cache(maxsize=1)
    def get_all_customers(self):
        """Get all customers with caching"""
        cache_key = self._get_cache_key('customers')  # This changes when customers are modified
        return list(self.customers.values())
    
    @lru_cache(maxsize=16)
    def get_customers_by_agent(self, agent_id):
        """Get customers by agent ID with caching"""
        cache_key = self._get_cache_key('customers')  # This changes when customers are modified
        return [c for c in self.customers.values() if c.agent_id == agent_id]
    
    # Product methods
    @lru_cache(maxsize=64)
    def get_product_by_id(self, product_id):
        """Get a product by ID with caching"""
        return self.products.get(product_id)
    
    def add_product(self, product):
        """Add a new product with automatic ID assignment"""
        if product.id is None:
            product.id = max(self.products.keys(), default=0) + 1
        self.products[product.id] = product
        self._invalidate_cache('products')
        return product
    
    def update_product(self, product):
        """Update an existing product"""
        if product.id in self.products:
            self.products[product.id] = product
            self._invalidate_cache('products')
            return product
        return None
    
    def delete_product(self, product_id):
        """Delete a product by ID and invalidate cache"""
        if product_id in self.products:
            del self.products[product_id]
            self._invalidate_cache('products')
            return True
        return False
    
    @lru_cache(maxsize=1)
    def get_all_products(self):
        """Get all products with caching"""
        cache_key = self._get_cache_key('products')  # This changes when products are modified
        return list(self.products.values())
    
    # Price list methods
    @lru_cache(maxsize=32)
    def get_price_list_by_id(self, price_list_id):
        """Get a price list by ID with caching"""
        return self.price_lists.get(price_list_id)
    
    def add_price_list(self, price_list):
        """Add a new price list with automatic ID assignment"""
        if price_list.id is None:
            price_list.id = max(self.price_lists.keys(), default=0) + 1
        self.price_lists[price_list.id] = price_list
        self._invalidate_cache('price_lists')
        return price_list
    
    def update_price_list(self, price_list):
        """Update an existing price list"""
        if price_list.id in self.price_lists:
            self.price_lists[price_list.id] = price_list
            self._invalidate_cache('price_lists')
            return price_list
        return None
    
    def delete_price_list(self, price_list_id):
        """Delete a price list by ID and invalidate cache"""
        if price_list_id in self.price_lists:
            del self.price_lists[price_list_id]
            self._invalidate_cache('price_lists')
            return True
        return False
    
    @lru_cache(maxsize=32)
    def get_price_lists_by_customer(self, customer_id):
        """Get price lists for a customer with caching"""
        cache_key = self._get_cache_key('price_lists')  # This changes when price lists are modified
        return [pl for pl in self.price_lists.values() if pl.customer_id == customer_id]
    
    @lru_cache(maxsize=64)
    def get_price_for_customer_product(self, customer_id, product_id):
        """Get the price for a specific customer and product with caching"""
        cache_key = self._get_cache_key('price_lists')  # This changes when price lists are modified
        
        # Create a dictionary for faster lookup
        customer_product_prices = {
            (pl.customer_id, pl.product_id): pl.custom_price 
            for pl in self.price_lists.values()
        }
        
        # Look for a custom price
        price = customer_product_prices.get((customer_id, product_id))
        if price is not None:
            return price
            
        # Return standard price if no custom price exists
        product = self.get_product_by_id(product_id)
        return product.price if product else None
    
    # Order methods
    @lru_cache(maxsize=64)
    def get_order_by_id(self, order_id):
        """Get an order by ID with caching"""
        return self.orders.get(order_id)
    
    def add_order(self, order):
        """Add a new order with automatic ID assignment"""
        if order.id is None:
            order.id = max(self.orders.keys(), default=0) + 1
        self.orders[order.id] = order
        self._invalidate_cache('orders')
        return order
    
    def update_order(self, order):
        """Update an existing order"""
        if order.id in self.orders:
            order.updated_at = datetime.now()
            self.orders[order.id] = order
            self._invalidate_cache('orders')
            return order
        return None
    
    def delete_order(self, order_id):
        """Delete an order by ID and its related items, and invalidate cache"""
        if order_id in self.orders:
            # Also delete related order items
            for item_id, item in list(self.order_items.items()):
                if item.order_id == order_id:
                    del self.order_items[item_id]
            # Delete the order
            del self.orders[order_id]
            self._invalidate_cache('orders')
            self._invalidate_cache('order_items')
            return True
        return False
    
    @lru_cache(maxsize=1)
    def get_all_orders(self):
        """Get all orders with caching"""
        cache_key = self._get_cache_key('orders')  # This changes when orders are modified
        return list(self.orders.values())
    
    @lru_cache(maxsize=32)
    def get_orders_by_user(self, user_id):
        """Get orders by user ID with caching"""
        cache_key = self._get_cache_key('orders')  # This changes when orders are modified
        return [o for o in self.orders.values() if o.user_id == user_id]
    
    @lru_cache(maxsize=32)
    def get_orders_by_customer(self, customer_id):
        """Get orders by customer ID with caching"""
        cache_key = self._get_cache_key('orders')  # This changes when orders are modified
        return [o for o in self.orders.values() if o.customer_id == customer_id]
    
    @lru_cache(maxsize=16)
    def get_orders_by_agent(self, agent_id):
        """Get orders for all customers of an agent with caching"""
        orders_cache_key = self._get_cache_key('orders')  # This changes when orders are modified
        customers_cache_key = self._get_cache_key('customers')  # This changes when customers are modified
        
        # Get all customers for this agent (already cached by get_customers_by_agent)
        agent_customers = {c.id for c in self.get_customers_by_agent(agent_id)}
        
        # Filter orders more efficiently
        return [o for o in self.orders.values() if o.customer_id in agent_customers]
    
    # Order item methods
    @lru_cache(maxsize=64)
    def get_order_item_by_id(self, order_item_id):
        """Get an order item by ID with caching"""
        return self.order_items.get(order_item_id)
    
    def add_order_item(self, order_item):
        """Add a new order item with automatic ID assignment"""
        if order_item.id is None:
            order_item.id = max(self.order_items.keys(), default=0) + 1
        self.order_items[order_item.id] = order_item
        self._invalidate_cache('order_items')
        return order_item
    
    def update_order_item(self, order_item):
        """Update an existing order item"""
        if order_item.id in self.order_items:
            self.order_items[order_item.id] = order_item
            self._invalidate_cache('order_items')
            return order_item
        return None
    
    def delete_order_item(self, order_item_id):
        """Delete an order item by ID and invalidate cache"""
        if order_item_id in self.order_items:
            del self.order_items[order_item_id]
            self._invalidate_cache('order_items')
            return True
        return False
    
    @lru_cache(maxsize=64)
    def get_items_by_order(self, order_id):
        """Get all items for an order with caching"""
        cache_key = self._get_cache_key('order_items')  # This changes when order items are modified
        return [i for i in self.order_items.values() if i.order_id == order_id]
    
    # Payment methods
    @lru_cache(maxsize=32)
    def get_payment_by_id(self, payment_id):
        """Get a payment by ID with caching"""
        return self.payments.get(payment_id)
    
    def add_payment(self, payment):
        """Add a new payment with automatic ID assignment"""
        if payment.id is None:
            payment.id = max(self.payments.keys(), default=0) + 1
        self.payments[payment.id] = payment
        self._invalidate_cache('payments')
        return payment
    
    def update_payment(self, payment):
        """Update an existing payment"""
        if payment.id in self.payments:
            self.payments[payment.id] = payment
            self._invalidate_cache('payments')
            return payment
        return None
    
    def delete_payment(self, payment_id):
        """Delete a payment by ID and invalidate cache"""
        if payment_id in self.payments:
            del self.payments[payment_id]
            self._invalidate_cache('payments')
            return True
        return False
    
    @lru_cache(maxsize=32)
    def get_payments_by_order(self, order_id):
        """Get all payments for an order with caching"""
        cache_key = self._get_cache_key('payments')  # This changes when payments are modified
        return [p for p in self.payments.values() if p.order_id == order_id]
    
    # Analytical methods
    @lru_cache(maxsize=32)
    def get_total_sales_by_user(self, user_id, start_date=None, end_date=None):
        """Calculate total sales by user in a date range with caching"""
        # Convert date parameters to strings for caching
        start_str = start_date.isoformat() if start_date else None
        end_str = end_date.isoformat() if end_date else None
        cache_key = f"sales_user_{user_id}_{start_str}_{end_str}_{self._get_cache_key('orders')}_{self._get_cache_key('order_items')}"
        
        # Get filtered orders by date range
        orders = [
            order for order in self.get_orders_by_user(user_id)
            if (start_date is None or order.order_date >= start_date) and
               (end_date is None or order.order_date <= end_date)
        ]
        
        # Calculate total sales more efficiently
        total = 0
        for order in orders:
            for item in self.get_items_by_order(order.id):
                total += item.total  # Using the property from OrderItem
        
        return total
    
    @lru_cache(maxsize=32)
    def get_total_sales_by_agent(self, agent_id, start_date=None, end_date=None):
        """Calculate total sales by agent in a date range with caching"""
        # Convert date parameters to strings for caching
        start_str = start_date.isoformat() if start_date else None
        end_str = end_date.isoformat() if end_date else None
        cache_key = f"sales_agent_{agent_id}_{start_str}_{end_str}_{self._get_cache_key('orders')}_{self._get_cache_key('order_items')}"
        
        # Get filtered orders by date range
        orders = [
            order for order in self.get_orders_by_agent(agent_id)
            if (start_date is None or order.order_date >= start_date) and
               (end_date is None or order.order_date <= end_date)
        ]
        
        # Calculate total sales more efficiently
        total = 0
        for order in orders:
            for item in self.get_items_by_order(order.id):
                total += item.total  # Using the property from OrderItem
        
        return total
    
    @lru_cache(maxsize=32)
    def get_total_commissions_by_user(self, user_id, start_date=None, end_date=None):
        """Calculate total commissions by user in a date range with caching"""
        # Convert date parameters to strings for caching
        start_str = start_date.isoformat() if start_date else None
        end_str = end_date.isoformat() if end_date else None
        cache_key = f"commission_user_{user_id}_{start_str}_{end_str}_{self._get_cache_key('orders')}_{self._get_cache_key('order_items')}"
        
        # Get filtered orders by date range
        orders = [
            order for order in self.get_orders_by_user(user_id)
            if (start_date is None or order.order_date >= start_date) and
               (end_date is None or order.order_date <= end_date)
        ]
        
        # Calculate total commissions more efficiently
        total = 0
        for order in orders:
            for item in self.get_items_by_order(order.id):
                total += item.commission_amount  # Using the property from OrderItem
        
        return total
    
    @lru_cache(maxsize=16)
    def get_monthly_sales_data(self, user_id=None, agent_id=None, year=None):
        """Get monthly sales data with caching"""
        # Set default year if not provided
        if year is None:
            year = datetime.now().year
        
        # Create cache key based on parameters
        cache_key = f"monthly_sales_{user_id}_{agent_id}_{year}_{self._get_cache_key('orders')}_{self._get_cache_key('order_items')}"
        
        monthly_data = [0] * 12  # Initialize with zeros for each month
        
        # Determine which orders to check (already cached)
        if user_id:
            orders = self.get_orders_by_user(user_id)
        elif agent_id:
            orders = self.get_orders_by_agent(agent_id)
        else:
            orders = self.get_all_orders()
        
        # Pre-filter orders by year for efficiency
        filtered_orders = [o for o in orders if o.order_date.year == year]
        
        # Group orders by month for more efficient processing
        orders_by_month = {}
        for order in filtered_orders:
            month_idx = order.order_date.month - 1  # 0-indexed
            if month_idx not in orders_by_month:
                orders_by_month[month_idx] = []
            orders_by_month[month_idx].append(order)
        
        # Calculate monthly totals
        for month_idx, month_orders in orders_by_month.items():
            for order in month_orders:
                for item in self.get_items_by_order(order.id):
                    monthly_data[month_idx] += item.total  # Using the property from OrderItem
        
        return monthly_data

# Initialize the storage
db = Storage()
