from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)
app.secret_key = "canteen_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    food_item = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    token = db.Column(db.String(20))
    status = db.Column(db.String(50))


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            error = "Please register first"

        elif user.password != password:
            error = "Invalid email id or password"

        else:
            session['user'] = user.name
            return redirect('/dashboard')

    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('menu.html', student=session['user'])

    return redirect('/login')
@app.route('/order', methods=['POST'])
def order():
    if 'user' in session:
        food = request.form['food']
        quantity = request.form['quantity']

        token = "C" + str(random.randint(100, 999))

        new_order = Order(
            student_name=session['user'],
            food_item=food,
            quantity=quantity,
            token=token,
            status="Preparing"
        )

        db.session.add(new_order)
        db.session.commit()

        return f"""
        <h1>Order Placed Successfully!</h1>
        <h2>Token Number: {token}</h2>
        <p>Food Item: {food}</p>
        <p>Quantity: {quantity}</p>
        <p>Status: Preparing</p>
        <a href='/dashboard'>Back to Menu</a>
        """

    return redirect('/login')
class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    message = db.Column(db.String(500))

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    rating = db.Column(db.Integer)
    review = db.Column(db.String(500))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = username
            return redirect('/admin')

        return "Invalid Admin Login"

    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if 'admin' in session:
        orders = Order.query.all()
        return render_template('admin_dashboard.html', orders=orders)

    return redirect('/admin_login')

@app.route('/update_status/<int:order_id>')
def update_status(order_id):
    order = Order.query.get(order_id)

    if order.status == "Preparing":
        order.status = "Ready"

    elif order.status == "Ready":
        order.status = "Delivered"

    db.session.commit()

    return redirect('/admin')
@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'user' in session:
        if request.method == 'POST':
            message = request.form['message']

            new_complaint = Complaint(
                student_name=session['user'],
                message=message
            )

            db.session.add(new_complaint)
            db.session.commit()

            return "<h1>Complaint Submitted Successfully!</h1><a href='/dashboard'>Back</a>"

        return render_template('complaints.html')

    return redirect('/login')
@app.route('/view_complaints')
def view_complaints():
    if 'admin' in session:
        complaints = Complaint.query.all()
        return render_template('view_complaints.html', complaints=complaints)

    return redirect('/admin_login')

@app.route('/review', methods=['GET', 'POST'])
def review():
    if 'user' in session:
        if request.method == 'POST':
            rating = request.form['rating']
            review_text = request.form['review']

            new_review = Review(
                student_name=session['user'],
                rating=rating,
                review=review_text
            )

            db.session.add(new_review)
            db.session.commit()

            return "<h1>Review Submitted Successfully!</h1><a href='/dashboard'>Back</a>"

        return render_template('reviews.html')

    return redirect('/login')

@app.route('/view_reviews')
def view_reviews():
    reviews = Review.query.all()
    return render_template('view_reviews.html', reviews=reviews)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)

