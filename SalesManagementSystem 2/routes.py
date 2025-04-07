from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
from auth import login_user, logout_user, login_required, admin_required, agent_required, can_view_customer, can_view_order
from models import User, Customer, Product, PriceList, Order, OrderItem, Payment
from storage import db
from utils import format_currency, format_date, get_order_total, get_order_paid_amount, get_order_balance, get_order_with_details, get_customer_orders, calculate_commission
from forms import (
    LoginForm, CustomerForm, ProductForm, OrderForm, 
    OrderItemForm, PaymentForm, PriceListForm
)

# Register custom filters
app.jinja_env.filters['currency'] = format_currency
app.jinja_env.filters['format_date'] = format_date

@app.context_processor
def inject_context():
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'now': datetime.now()
    }

# Public routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        success, token = login_user(username, password)
        if success:
            return redirect(url_for('dashboard'))
        else:
            flash('Nome utente o password non validi', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('Hai effettuato il logout correttamente', 'success')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    role = session.get('role')
    
    # Get stats for the current month
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)
    
    if role == 'admin':
        all_orders = db.get_all_orders()
        customers_count = len(db.get_all_customers())
        users_count = len(db.get_all_users())
    elif role == 'agent':
        all_orders = db.get_orders_by_agent(user_id)
        customers_count = len(db.get_customers_by_agent(user_id))
        users_count = len(db.get_collaborators_by_agent(user_id)) + 1  # +1 for the agent
    else:  # collaborator
        all_orders = db.get_orders_by_user(user_id)
        agent_id = session.get('agent_id')
        customers_count = len(db.get_customers_by_agent(agent_id))
        users_count = 1  # Just themselves
    
    # Filter orders for the current month
    month_orders = [o for o in all_orders if o.order_date.month == now.month and o.order_date.year == now.year]
    
    # Calculate total sales
    total_sales = 0
    for order in month_orders:
        total_sales += get_order_total(order.id)
    
    # Get recent orders
    recent_orders = sorted(all_orders, key=lambda o: o.order_date, reverse=True)[:5]
    recent_orders_with_details = []
    
    for order in recent_orders:
        customer = db.get_customer_by_id(order.customer_id)
        order_dict = order.to_dict()
        order_dict['customer_name'] = customer.name if customer else "Unknown"
        order_dict['total_amount'] = get_order_total(order.id)
        recent_orders_with_details.append(order_dict)
    
    # Get sales data for chart
    sales_data = db.get_monthly_sales_data(
        user_id=user_id if role == 'collaborator' else None,
        agent_id=user_id if role == 'agent' else (session.get('agent_id') if role == 'collaborator' else None),
        year=now.year
    )
    
    # Get commission data
    commission_info = calculate_commission(user_id, first_day, now)
    
    return render_template(
        'dashboard.html',
        orders_count=len(month_orders),
        customers_count=customers_count,
        users_count=users_count,
        total_sales=total_sales,
        recent_orders=recent_orders_with_details,
        sales_data=sales_data,
        commission_info=commission_info
    )

# Customers routes
@app.route('/customers')
@login_required
def customers_list():
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'admin':
        customers = db.get_all_customers()
    elif role == 'agent':
        customers = db.get_customers_by_agent(user_id)
    else:  # collaborator
        agent_id = session.get('agent_id')
        customers = db.get_customers_by_agent(agent_id)
    
    return render_template('customers.html', customers=customers)

@app.route('/customers/new', methods=['GET', 'POST'])
@agent_required
def customer_new():
    form = CustomerForm()
    if request.method == 'POST':
        user_id = session.get('user_id')
        agent_id = user_id if session.get('role') == 'agent' else session.get('agent_id')
        
        customer = Customer(
            id=None,
            name=request.form.get('name'),
            vat_number=request.form.get('vat_number'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            zip_code=request.form.get('zip_code'),
            country=request.form.get('country'),
            contact_person=request.form.get('contact_person'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            agent_id=agent_id
        )
        
        db.add_customer(customer)
        flash('Cliente aggiunto con successo', 'success')
        return redirect(url_for('customers_list'))
    
    return render_template('customer_detail.html', customer=None, is_new=True, form=form)

@app.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    if not can_view_customer(customer_id):
        flash('Non hai il permesso di visualizzare questo cliente', 'danger')
        return redirect(url_for('customers_list'))
    
    customer = db.get_customer_by_id(customer_id)
    if not customer:
        flash('Cliente non trovato', 'danger')
        return redirect(url_for('customers_list'))
    
    orders = get_customer_orders(customer_id)
    
    # Get custom price lists for the customer
    price_lists = db.get_price_lists_by_customer(customer_id)
    price_list_items = []
    
    for pl in price_lists:
        product = db.get_product_by_id(pl.product_id)
        if product:
            price_list_items.append({
                'id': pl.id,
                'product_id': pl.product_id,
                'product_name': product.name,
                'standard_price': product.price,
                'custom_price': pl.custom_price
            })
    
    # Get all products for the custom price list form
    products = db.get_all_products()
    
    return render_template(
        'customer_detail.html',
        customer=customer,
        is_new=False,
        orders=orders,
        price_list_items=price_list_items,
        products=products
    )

@app.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@agent_required
def customer_edit(customer_id):
    customer = db.get_customer_by_id(customer_id)
    if not customer:
        flash('Cliente non trovato', 'danger')
        return redirect(url_for('customers_list'))
    
    if not can_view_customer(customer_id):
        flash('Non hai il permesso di modificare questo cliente', 'danger')
        return redirect(url_for('customers_list'))
    
    form = CustomerForm()
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.vat_number = request.form.get('vat_number')
        customer.address = request.form.get('address')
        customer.city = request.form.get('city')
        customer.zip_code = request.form.get('zip_code')
        customer.country = request.form.get('country')
        customer.contact_person = request.form.get('contact_person')
        customer.email = request.form.get('email')
        customer.phone = request.form.get('phone')
        
        db.update_customer(customer)
        flash('Cliente aggiornato con successo', 'success')
        return redirect(url_for('customer_detail', customer_id=customer_id))
    
    # Get all products for the custom price list form
    products = db.get_all_products()
    return render_template('customer_detail.html', customer=customer, is_new=False, is_edit=True, form=form, products=products)

@app.route('/customers/<int:customer_id>/delete', methods=['POST'])
@agent_required
def customer_delete(customer_id):
    if not can_view_customer(customer_id):
        flash('Non hai il permesso di eliminare questo cliente', 'danger')
        return redirect(url_for('customers_list'))
    
    if db.delete_customer(customer_id):
        flash('Cliente eliminato con successo', 'success')
    else:
        flash('Impossibile eliminare il cliente', 'danger')
    
    return redirect(url_for('customers_list'))

@app.route('/customers/<int:customer_id>/price_list', methods=['POST'])
@agent_required
def customer_price_list_add(customer_id):
    if not can_view_customer(customer_id):
        flash('Non hai il permesso di modificare questo cliente', 'danger')
        return redirect(url_for('customer_detail', customer_id=customer_id))
    
    product_id = request.form.get('product_id', type=int)
    custom_price = request.form.get('custom_price', type=float)
    
    # Check if product exists
    product = db.get_product_by_id(product_id)
    if not product:
        flash('Prodotto non trovato', 'danger')
        return redirect(url_for('customer_detail', customer_id=customer_id))
    
    # Check if price list already exists for this product
    for pl in db.get_price_lists_by_customer(customer_id):
        if pl.product_id == product_id:
            pl.custom_price = custom_price
            db.update_price_list(pl)
            flash('Prezzo personalizzato aggiornato con successo', 'success')
            return redirect(url_for('customer_detail', customer_id=customer_id))
    
    # Create new price list
    price_list = PriceList(
        id=None,
        customer_id=customer_id,
        product_id=product_id,
        custom_price=custom_price
    )
    
    db.add_price_list(price_list)
    flash('Prezzo personalizzato aggiunto con successo', 'success')
    return redirect(url_for('customer_detail', customer_id=customer_id))

# Products routes
@app.route('/products')
@login_required
def products_list():
    products = db.get_all_products()
    return render_template('products.html', products=products)

@app.route('/products/new', methods=['GET', 'POST'])
@admin_required
def product_new():
    form = ProductForm()
    if request.method == 'POST':
        product = Product(
            id=None,
            name=request.form.get('name'),
            code=request.form.get('code'),
            description=request.form.get('description'),
            price=float(request.form.get('price', 0)),
            unit=request.form.get('unit'),
            category=request.form.get('category')
        )
        
        db.add_product(product)
        flash('Prodotto aggiunto con successo', 'success')
        return redirect(url_for('products_list'))
    
    return render_template('product_detail.html', product=None, is_new=True, form=form)

@app.route('/products/<int:product_id>')
@login_required
def product_detail(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        flash('Prodotto non trovato', 'danger')
        return redirect(url_for('products_list'))
    
    return render_template('product_detail.html', product=product, is_new=False)

@app.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@admin_required
def product_edit(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        flash('Prodotto non trovato', 'danger')
        return redirect(url_for('products_list'))
    
    form = ProductForm()
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.code = request.form.get('code')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.unit = request.form.get('unit')
        product.category = request.form.get('category')
        
        db.update_product(product)
        flash('Prodotto aggiornato con successo', 'success')
        return redirect(url_for('product_detail', product_id=product_id))
    
    return render_template('product_detail.html', product=product, is_new=False, is_edit=True, form=form)

@app.route('/products/<int:product_id>/delete', methods=['POST'])
@admin_required
def product_delete(product_id):
    if db.delete_product(product_id):
        flash('Prodotto eliminato con successo', 'success')
    else:
        flash('Impossibile eliminare il prodotto', 'danger')
    
    return redirect(url_for('products_list'))

# Orders routes
@app.route('/orders')
@login_required
def orders_list():
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'admin':
        orders = db.get_all_orders()
    elif role == 'agent':
        orders = db.get_orders_by_agent(user_id)
    else:  # collaborator
        orders = db.get_orders_by_user(user_id)
    
    orders_with_details = []
    for order in orders:
        customer = db.get_customer_by_id(order.customer_id)
        order_dict = order.to_dict()
        order_dict['customer_name'] = customer.name if customer else "Unknown"
        order_dict['total_amount'] = get_order_total(order.id)
        orders_with_details.append(order_dict)
    
    return render_template('orders.html', orders=orders_with_details)

@app.route('/orders/new', methods=['GET', 'POST'])
@login_required
def order_new():
    form = OrderForm()
    role = session.get('role')
    user_id = session.get('user_id')
    
    # Get customers based on user role
    if role == 'admin':
        customers = db.get_all_customers()
    elif role == 'agent':
        customers = db.get_customers_by_agent(user_id)
    else:  # collaborator
        agent_id = session.get('agent_id')
        customers = db.get_customers_by_agent(agent_id)
    
    products = db.get_all_products()
    
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id'))
        
        # Verify the user can create orders for this customer
        if not can_view_customer(customer_id):
            flash('Non hai il permesso di creare ordini per questo cliente', 'danger')
            return redirect(url_for('orders_list'))
        
        # Il codice univoco verrà generato automaticamente
        order = Order(
            id=None,
            customer_id=customer_id,
            order_date=datetime.now(),
            user_id=user_id,
            status=request.form.get('status', 'pending'),
            notes=request.form.get('notes')
        )
        
        # Add the order
        order = db.add_order(order)
        
        # Add order items from form data
        item_count = int(request.form.get('item_count', 0))
        
        # Log all form data for debugging
        print("==== ORDER FORM DATA START ====")
        for key, value in request.form.items():
            print(f"Field: {key}, Value: {value}")
        print("==== ORDER FORM DATA END ====")
        
        for i in range(item_count):
            try:
                product_id = int(request.form.get(f'product_id_{i}'))
                quantity = int(request.form.get(f'quantity_{i}'))
                price = float(request.form.get(f'price_{i}'))
                commission_rate = float(request.form.get(f'commission_rate_{i}', 0.0))
                
                # Print debugging information
                print(f"Processing item {i}")
                print(f"Product ID: {product_id}")
                print(f"Quantity: {quantity}")
                print(f"Price: {price}")
                print(f"Commission Rate: {commission_rate}")
            except (ValueError, TypeError) as e:
                print(f"Error processing item {i}: {str(e)}")
                continue
            
            if product_id and quantity > 0:
                try:
                    # Prima di creare l'item, verifica che l'ordine esista ancora
                    order_check = db.get_order_by_id(order.id)
                    if not order_check:
                        print(f"ERRORE: Ordine {order.id} non trovato nel database durante l'aggiunta dell'articolo")
                        continue
                    
                    order_item = OrderItem(
                        id=None,
                        order_id=order.id,
                        product_id=product_id,
                        quantity=quantity,
                        price=price,
                        commission_rate=commission_rate
                    )
                    print(f"Aggiunta item all'ordine {order.id}: Prodotto={product_id}, Quantità={quantity}, Prezzo={price}")
                    
                    # Verifica che l'item abbia tutti i campi corretti prima di aggiungerlo
                    if order_item.order_id is None or order_item.product_id is None:
                        print(f"ERRORE: Dati item incompleti - order_id={order_item.order_id}, product_id={order_item.product_id}")
                        continue
                        
                    # Aggiungi l'item all'ordine
                    result_item = db.add_order_item(order_item)
                    print(f"Item aggiunto con successo, ID: {result_item.id}")
                except Exception as e:
                    print(f"ECCEZIONE durante l'aggiunta dell'item: {str(e)}")
                    continue
        
        flash('Ordine creato con successo', 'success')
        return redirect(url_for('order_detail', order_id=order.id))
    
    return render_template('order_detail.html', order=None, is_new=True, customers=customers, products=products, form=form)

@app.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    if not can_view_order(order_id):
        flash('Non hai il permesso di visualizzare questo ordine', 'danger')
        return redirect(url_for('orders_list'))
    
    order_details = get_order_with_details(order_id)
    if not order_details:
        flash('Ordine non trovato', 'danger')
        return redirect(url_for('orders_list'))
    
    # Get payments for this order
    payments = db.get_payments_by_order(order_id)
    
    return render_template('order_detail.html', order=order_details, is_new=False, payments=payments)

@app.route('/orders/<int:order_id>/edit', methods=['GET', 'POST'])
@login_required
def order_edit(order_id):
    if not can_view_order(order_id):
        flash('Non hai il permesso di modificare questo ordine', 'danger')
        return redirect(url_for('orders_list'))
    
    order = db.get_order_by_id(order_id)
    if not order:
        flash('Ordine non trovato', 'danger')
        return redirect(url_for('orders_list'))
    
    form = OrderForm()
    if request.method == 'POST':
        order.status = request.form.get('status')
        order.notes = request.form.get('notes')
        order.updated_at = datetime.now()
        
        db.update_order(order)
        flash('Ordine aggiornato con successo', 'success')
        return redirect(url_for('order_detail', order_id=order_id))
    
    order_details = get_order_with_details(order_id)
    customers = []
    products = db.get_all_products()
    
    return render_template('order_detail.html', order=order_details, is_new=False, is_edit=True, customers=customers, products=products, form=form)

@app.route('/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def order_delete(order_id):
    if not can_view_order(order_id):
        flash('Non hai il permesso di eliminare questo ordine', 'danger')
        return redirect(url_for('orders_list'))
    
    if db.delete_order(order_id):
        flash('Ordine eliminato con successo', 'success')
    else:
        flash('Impossibile eliminare l\'ordine', 'danger')
    
    return redirect(url_for('orders_list'))

@app.route('/orders/<int:order_id>/add_payment', methods=['POST'])
@login_required
def order_add_payment(order_id):
    if not can_view_order(order_id):
        flash('Non hai il permesso di modificare questo ordine', 'danger')
        return redirect(url_for('order_detail', order_id=order_id))
    
    amount = float(request.form.get('amount', 0))
    payment_date = datetime.now()
    payment_method = request.form.get('payment_method')
    notes = request.form.get('payment_notes')
    
    payment = Payment(
        id=None,
        order_id=order_id,
        amount=amount,
        payment_date=payment_date,
        payment_method=payment_method,
        notes=notes
    )
    
    db.add_payment(payment)
    flash('Pagamento aggiunto con successo', 'success')
    return redirect(url_for('order_detail', order_id=order_id))

# Reports routes
@app.route('/reports')
@login_required
def reports():
    user_id = session.get('user_id')
    role = session.get('role')
    
    now = datetime.now()
    year = now.year
    
    # Get monthly sales data
    if role == 'admin':
        sales_data = db.get_monthly_sales_data(year=year)
        user_list = db.get_all_users()
    elif role == 'agent':
        sales_data = db.get_monthly_sales_data(agent_id=user_id, year=year)
        user_list = db.get_collaborators_by_agent(user_id)
        user_list.append(db.get_user_by_id(user_id))  # Add the agent to the list
    else:  # collaborator
        sales_data = db.get_monthly_sales_data(user_id=user_id, year=year)
        user_list = [db.get_user_by_id(user_id)]  # Just the collaborator
    
    # Calculate commission for each user
    user_commissions = []
    for user in user_list:
        if role == 'admin' or (role == 'agent' and user.id == user_id) or user.id == user_id:
            commission_info = calculate_commission(user.id)
            user_commissions.append({
                'id': user.id,
                'name': user.full_name or user.username,
                'role': user.role,
                'total_sales': commission_info['total_sales'],
                'total_commission': commission_info['total_commission']
            })
    
    return render_template('reports.html', sales_data=sales_data, user_commissions=user_commissions)

# API endpoints for AJAX requests
@app.route('/api/products/<int:product_id>')
@login_required
def api_product_detail(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return jsonify({'error': 'Prodotto non trovato'}), 404
    
    return jsonify(product.to_dict())

@app.route('/api/customers/<int:customer_id>/price/<int:product_id>')
@login_required
def api_customer_price(customer_id, product_id):
    if not can_view_customer(customer_id):
        return jsonify({'error': 'Permesso negato'}), 403
    
    price = db.get_price_for_customer_product(customer_id, product_id)
    if price is None:
        return jsonify({'error': 'Prezzo non trovato'}), 404
    
    return jsonify({'price': price})

@app.route('/api/customers/<int:customer_id>/price-list')
@login_required
def api_customer_price_list(customer_id):
    if not can_view_customer(customer_id):
        return jsonify({'error': 'Permesso negato'}), 403
    
    # Ottieni tutti i prodotti
    all_products = db.get_all_products()
    products_with_prices = []
    
    # Ottieni il listino prezzi personalizzato per questo cliente
    custom_price_list = db.get_price_lists_by_customer(customer_id)
    custom_prices = {item.product_id: item.custom_price for item in custom_price_list}
    
    # Prepara i dati dei prodotti con i prezzi personalizzati
    for product in all_products:
        product_dict = product.to_dict()
        # Se esiste un prezzo personalizzato per questo prodotto, usalo
        if product.id in custom_prices:
            product_dict['price'] = custom_prices[product.id]
            product_dict['has_custom_price'] = True
            products_with_prices.append(product_dict)
        # Se il cliente non ha un listino prezzi personalizzato, mostra tutti i prodotti
        elif not custom_prices:
            product_dict['has_custom_price'] = False
            products_with_prices.append(product_dict)
    
    return jsonify(products_with_prices)

@app.route('/api/orders/<int:order_id>/items')
@login_required
def api_order_items(order_id):
    if not can_view_order(order_id):
        return jsonify({'error': 'Permesso negato'}), 403
    
    items = get_order_items_with_details(order_id)
    return jsonify(items)
