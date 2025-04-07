from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, FloatField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class CustomerForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    vat_number = StringField('VAT Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    zip_code = StringField('ZIP/Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[Optional()])
    email = EmailField('Email', validators=[Optional(), Email()])
    phone = TelField('Phone', validators=[Optional()])
    submit = SubmitField('Save Customer')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    code = StringField('Product Code', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    unit = StringField('Unit', validators=[DataRequired()])
    category = StringField('Category', validators=[Optional()])
    submit = SubmitField('Save Product')

class OrderForm(FlaskForm):
    customer_id = SelectField('Customer', validators=[DataRequired()], coerce=int)
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Order')

class OrderItemForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()], coerce=int)
    quantity = FloatField('Quantity', validators=[DataRequired(), NumberRange(min=0.01)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    commission_rate = FloatField('Commission Rate (%)', validators=[DataRequired(), NumberRange(min=0, max=100)], default=0)
    submit = SubmitField('Add Item')

class PaymentForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    payment_method = SelectField('Payment Method', choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Add Payment')

class PriceListForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()], coerce=int)
    custom_price = FloatField('Custom Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Custom Price')