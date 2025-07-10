import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv() # take environment variables from .env.

import google.generativeai as genai

GEMINI_API_KEY = ""
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set. Gemini API calls will fail.")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:marco@localhost:5432/mydatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.email}')"

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_fullname'] = user.fullname
        session['user_email'] = user.email
        flash('Login successful! 🌿', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Login failed. Check your email and password.', 'danger')
        return redirect(url_for('home'))

@app.route('/signup', methods=['POST'])
def signup():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')

    if not all([fullname, email, password]):
        flash('All fields are required for signup.', 'danger')
        return redirect(url_for('home'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('An account with this email already exists. Please log in.', 'warning')
        return redirect(url_for('home'))

    new_user = User(fullname=fullname, email=email)
    new_user.set_password(password)

    try:
        db.session.add(new_user)
        db.session.commit()
        flash('Signup successful! 🌱 Please log in.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        flash('An error occurred during signup. Please try again.', 'danger')

    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('home'))
    user_fullname = session.get('user_fullname', 'Guest')
    user_email = session.get('user_email', 'N/A')
    return render_template('dashboard.html', fullname=user_fullname, email=user_email)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_fullname', None)
    session.pop('user_email', None)
    flash('You have been logged out. 👋', 'info')
    return redirect(url_for('home'))


@app.route('/chat_with_gemini', methods=['POST'])
def chat_with_gemini():
    #return '<h>hello</h>'
    if not 'user_id' in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    #client = genai.Client()
    #response = client.models.generate_content(model="gemini-2.5-flash", contents="Explain how AI works in a few words")
    #print(response.text)

    try:
        print("Thinking...")
        response = model.generate_content(user_message)
        gemini_response_text = response.text
        print("Think Finished!")
        #print(gemini_response_text)
        #gemini_response_text = f"You asked: '{user_message}'. I am an AI, how can I help you further?"
        

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        gemini_response_text = "I'm sorry, I couldn't process that request right now."
        #print(gemini_response_text)
    # *******************************************************************

    return jsonify({'gemini_response': gemini_response_text})

    
if __name__ == '__main__':
    app.run(debug=True)
