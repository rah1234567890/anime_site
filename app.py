from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = 'animekey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    db.session.add(User(username=username, password=password))
    db.session.commit()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    user = User.query.filter_by(username=request.form['username'], password=request.form['password']).first()
    if user:
        session['username'] = user.username
        return redirect('/dashboard')
    return "Login Failed"

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', user=session['username'])
    return redirect('/')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if query:
        url = f'https://api.jikan.moe/v4/anime?q={query}'
        res = requests.get(url).json()
        return render_template('search.html', data=res['data'])
    return render_template('search.html', data=None)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
