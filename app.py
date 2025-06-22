from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", 'animekey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    if not username or not password:
        flash("Username and Password cannot be empty.", "danger")
        return redirect('/register')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        flash("Username already exists. Please login.", "warning")
        return redirect('/')
    db.session.add(User(username=username, password=password))
    db.session.commit()
    flash("Registration successful. Please login.", "success")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        session['username'] = user.username
        flash("Welcome back, " + user.username + "!", "success")
        return redirect('/dashboard')
    flash("Login failed. Check credentials.", "danger")
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', user=session['username'])
    flash("Please login to access the dashboard.", "warning")
    return redirect('/')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query:
        try:
            url = f'https://api.jikan.moe/v4/anime?q={query}'
            res = requests.get(url)
            res.raise_for_status()
            data = res.json().get('data', [])
            return render_template('search.html', data=data)
        except Exception as e:
            flash("Error fetching anime data.", "danger")
    return render_template('search.html', data=None)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "info")
    return redirect('/')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
