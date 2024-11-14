from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields, validate, ValidationError
from password import my_password

#---------------------------------------------------------------------------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{my_password}@localhost/e_commerce_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)

#---------------------------------------------------------------------------------------------------------------------------------

class CustomerSchema(ma.Schema):
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("name", "email", "phone", "id")

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")

class CustomerAccountSchema(ma.Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=1))
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("username", "password", "customer_id", "id")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)

#---------------------------------------------------------------------------------------------------------------------------------

class Customer (db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(320))
    phone = db.Column(db.String(15))
    customer_account = db.relationship('CustomerAccount', back_populates='customer')
    orders = db.relationship('Order', backref='customer')
    

class Order (db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))

class CustomerAccount (db.Model):
    __tablename__ = 'customer_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    customer = db.relationship('Customer', back_populates='customer_account')

order_product = db.Table('Order_Product',
        db.Column('order_id', db.Integer, db.ForeignKey('orders.id'), primary_key=True),
        db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Product (db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    orders = db.relationship('Order', secondary=order_product, backref=db.backref('products'))

#---------------------------------------------------------------------------------------------------------------------------------

@app.route('/')
def home():
    return 'Welcome to my Flask E Commerce Application'

#---------------------------------------------------------------------------------------------------------------------------------

@app.route("/customers", methods=["GET"])
def get_customers():
     customers = Customer.query.all()
     return customers_schema.jsonify(customers)

@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({"message":"New customer successfully added"}), 201

@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    customer.name = customer_data['name']
    customer.email = customer_data['email']
    customer.phone = customer_data['phone']
    db.session.commit()
    return jsonify({"message":"Customer updated successfully"}), 200

@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message":"Customer removed successfully"}), 200

@app.route("/customers/<int:id>", methods=['GET'])
def query_customer_by_id(id):
    customer=Customer.query.get_or_404(id)
    return customer_schema.jsonify(customer)

#---------------------------------------------------------------------------------------------------------------------------------

@app.route("/customer_accounts", methods=["POST"])
def add_customer_account():
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_customer_account = CustomerAccount(username=customer_account_data['username'], password=customer_account_data['password'], customer_id=customer_account_data['customer_id'])
    db.session.add(new_customer_account)
    db.session.commit()
    return jsonify({"message":"New customer account successfully added"}), 201

@app.route("/customer_accounts", methods=["GET"])
def get_customers_accounts():
     customer_accounts = CustomerAccount.query.all()
     return customer_accounts_schema.jsonify(customer_accounts)

@app.route("/customer_accounts/<int:id>", methods=['GET'])
def query_customer_account_by_id(id):
    customer_account=CustomerAccount.query.get_or_404(id)
    customer_details=customer_account.customer
    serialized_customer=customer_schema.dump(customer_details)
    serialized_customer_account=customer_account_schema.dump(customer_account)
    return jsonify({
        "customer":serialized_customer,
        "customer_account":serialized_customer_account
    })

@app.route("/customer_accounts/<int:id>", methods=["PUT"])
def update_customer_account(id):
    customer_account = CustomerAccount.query.get_or_404(id)
    try:
        customer_account_data = customer_account_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    customer_account.username = customer_account_data['username']
    customer_account.password = customer_account_data['password']
    customer_account.customer_id = customer_account_data['customer_id']
    db.session.commit()
    return jsonify({"message":"Customer Account updated successfully"}), 200

#---------------------------------------------------------------------------------------------------------------------------------

@app.route("/products", methods=["GET"])
def get_products():
     products = Product.query.all()
     return products_schema.jsonify(products)

@app.route("/products", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    new_product = Product(name=product_data['name'], price=product_data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message":"New product successfully added"}), 201

@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get_or_404(id)
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        print(f"Error: {e}")
        return jsonify(e.messages), 400
    
    product.name = product_data['name']
    product.price = product_data['price']
    db.session.commit()
    return jsonify({"message":"Product updated successfully"}), 200

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message":"Product removed successfully"}), 200

@app.route("/products/by-name", methods=['GET'])
def query_product_by_name():
    name=request.args.get('name')
    product=Product.query.filter(Product.name==name).first()
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404

#---------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------------
with app.app_context():
        db.create_all()

if __name__ == '__main__':
     app.run(debug=True)