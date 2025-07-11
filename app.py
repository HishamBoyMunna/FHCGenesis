import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


load_dotenv() # take environment variables from .env.

import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyD2bK8Rov5AQeiFwnevXIux8BeHOtMFoe0"
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

    devices = db.relationship('Device', backref='owner', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.fullname}', '{self.email}')"
# NEW Device Model
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # 'electric', 'water', 'waste'
    rating = db.Column(db.Float, nullable=False) # Device rating (kW for electric, L/min for water, etc.)
    unit = db.Column(db.String(20), nullable=False) # Unit of measurement (kW, L/min, kg/day, etc.)

    # Relationship to usage records
    usage_records = db.relationship('DeviceUsage', backref='device', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Device('{self.name}', '{self.type}', Rating: {self.rating} {self.unit})"

# NEW DeviceUsage Model
class DeviceUsage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    hours_used = db.Column(db.Float, nullable=False, default=0.0) # Hours used on this date
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"DeviceUsage(Device: {self.device_id}, Date: {self.date}, Hours: {self.hours_used})"


with app.app_context():
    db.create_all()

@app.route('/')
def home():
    print("[route] Calling root...")
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    print("[route] Calling login...")
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
    print("[route] Calling signup...")
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
    print("[route] Calling dashboard...")
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'danger')
        return redirect(url_for('home'))
    user_fullname = session.get('user_fullname', 'Guest')
    user_email = session.get('user_email', 'N/A')
    return render_template('dashboard.html', fullname=user_fullname, email=user_email)

@app.route('/logout')
def logout():
    print("[route] Calling logout...")
    session.pop('user_id', None)
    session.pop('user_fullname', None)
    session.pop('user_email', None)
    flash('You have been logged out. 👋', 'info')
    return redirect(url_for('home'))


@app.route('/chat_with_gemini', methods=['POST'])
def chat_with_gemini():
    print("[route] Calling gemini...")
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
        prompt = '''You are a smart, friendly, and insightful resource assistant named EcoBot. You help users monitor and manage their electricity, water, and waste usage. Your role is to make accurate predictions, offer personalized tips, and give insightful feedback based on user data.

A. Prediction and Estimation:
- Predict upcoming electricity, water, and waste bills based on usage history and tariff slabs.
- Offer what-if analysis. For example, if a user says “What if I reduce AC usage by 1 hour daily?”, respond with the estimated savings in units and money.

B. Smart Insights & Notifications:
- Provide insights like:
  - “You're using 20% more water this week than last week.”
  - “Your electricity usage peaks between 8 PM – 11 PM.”
  - “You can save ₹500/month by switching to LED lighting.”
- Compare current usage with past trends and notify about spikes or reductions.

C. Personalized Tips:
- Use information about the user's appliances, household size, and past usage to suggest actionable tips such as:
  - “Install aerators to reduce tap water usage by 30%.”
  - “Switch to inverter AC for 40% energy savings.”
  - “Segregate waste to avoid fines and increase recycling.”

System Instructions:
- Use a friendly and helpful tone.
- Always explain the benefit or reason behind a suggestion.
- Use localized currency (₹) and units (kWh, litres, kg).
- Encourage sustainable behavior subtly, without being forceful.

Goal: Help users understand, predict, and reduce their utility bills while improving sustainability.''' + user_message
        response = model.generate_content(prompt)
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

@app.route('/api/devices', methods=['GET'])
def get_devices():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    devices = Device.query.filter_by(user_id=user_id).all()

    devices_list = []
    for device in devices:
        devices_list.append({
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'rating': device.rating,
            'unit': device.unit
        })
    return jsonify(devices_list)

@app.route('/api/devices', methods=['POST'])
def add_device():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    data = request.get_json()
    name = data.get('name')
    device_type = data.get('type')
    rating = data.get('rating')
    unit = data.get('unit')

    if not name or not device_type or rating is None or unit is None:
        return jsonify({'error': 'Device name, type, rating, and unit are required'}), 400

    new_device = Device(user_id=user_id, name=name, type=device_type, rating=rating, unit=unit)
    try:
        db.session.add(new_device)
        db.session.commit()
        return jsonify({
            'message': 'Device added successfully',
            'device': {
                'id': new_device.id,
                'name': new_device.name,
                'type': new_device.type,
                'rating': new_device.rating,
                'unit': new_device.unit
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error adding device: {e}")
        return jsonify({'error': 'Failed to add device', 'details': str(e)}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()

    if not device:
        return jsonify({'error': 'Device not found or unauthorized'}), 404

    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting device: {e}")
        return jsonify({'error': 'Failed to delete device', 'details': str(e)}), 500

@app.route('/api/devices/<int:device_id>', methods=['PUT'])
def update_device_usage(device_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()

    if not device:
        return jsonify({'error': 'Device not found or unauthorized'}), 404

    data = request.get_json()
    hours_used = data.get('hours_used')

    if hours_used is None:
        return jsonify({'error': 'Hours used is required'}), 400

    try:
        # Validate that hours_used is a non-negative number
        if not isinstance(hours_used, (int, float)) or hours_used < 0:
            return jsonify({'error': 'Hours used must be a non-negative number'}), 400

        new_usage = DeviceUsage(device_id=device_id, date=datetime.utcnow().date(), hours_used=hours_used)
        db.session.add(new_usage)
        db.session.commit()
        
        return jsonify({
            'message': 'Device usage updated successfully',
            'usage_record': {
                'id': new_usage.id,
                'device_id': new_usage.device_id,
                'date': new_usage.date.strftime('%Y-%m-%d'),
                'hours_used': new_usage.hours_used
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating device usage: {e}")
        return jsonify({'error': 'Failed to update device usage', 'details': str(e)}), 500

@app.route('/api/devices/<int:device_id>/usage', methods=['GET'])
def get_device_usage(device_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()

    if not device:
        return jsonify({'error': 'Device not found or unauthorized'}), 404

    # Get usage records for the last 7 days
    from datetime import timedelta
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    
    usage_records = DeviceUsage.query.filter(
        DeviceUsage.device_id == device_id,
        DeviceUsage.date >= start_date,
        DeviceUsage.date <= end_date
    ).order_by(DeviceUsage.date).all()

    # Create a dictionary with dates as keys
    usage_data = {}
    current_date = start_date
    while current_date <= end_date:
        usage_data[current_date.strftime('%Y-%m-%d')] = 0.0
        current_date += timedelta(days=1)

    # Fill in actual usage data
    for record in usage_records:
        usage_data[record.date.strftime('%Y-%m-%d')] = record.hours_used

    return jsonify({
        'device': {
            'id': device.id,
            'name': device.name,
            'type': device.type,
            'rating': device.rating,
            'unit': device.unit
        },
        'usage_data': usage_data
    })

@app.route('/api/devices/<int:device_id>/usage', methods=['POST'])
def add_device_usage(device_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    device = Device.query.filter_by(id=device_id, user_id=user_id).first()

    if not device:
        return jsonify({'error': 'Device not found or unauthorized'}), 404

    data = request.get_json()
    date_str = data.get('date')
    hours_used = data.get('hours_used')

    if not date_str or hours_used is None:
        return jsonify({'error': 'Date and hours used are required'}), 400

    try:
        # Parse date
        usage_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Validate that hours_used is a non-negative number
        if not isinstance(hours_used, (int, float)) or hours_used < 0:
            return jsonify({'error': 'Hours used must be a non-negative number'}), 400

        # Check if usage record already exists for this date
        existing_usage = DeviceUsage.query.filter_by(device_id=device_id, date=usage_date).first()
        if existing_usage:
            existing_usage.hours_used = hours_used
        else:
            new_usage = DeviceUsage(device_id=device_id, date=usage_date, hours_used=hours_used)
            db.session.add(new_usage)

        db.session.commit()
        
        return jsonify({
            'message': 'Device usage added successfully',
            'usage_record': {
                'device_id': device_id,
                'date': usage_date.strftime('%Y-%m-%d'),
                'hours_used': hours_used
            }
        }), 201
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error adding device usage: {e}")
        return jsonify({'error': 'Failed to add device usage', 'details': str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    
    try:
        # Try to use Gemini API first, fall back to demo if not available
        try:
            from gemini_insights import get_gemini_insights
            print("[route] Thinking...")
            insights = get_gemini_insights()
            if insights:
                return jsonify({
                    'success': True,
                    'insights': insights,
                    'source': 'gemini'
                })
        except Exception as e:
            print(f"Gemini API not available, using demo insights: {e}")
        
        # Fall back to demo insights
        from gemini_insights_demo import get_demo_insights
        insights = get_demo_insights()
        
        if insights:
            return jsonify({
                'success': True,
                'insights': insights,
                'source': 'demo'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate insights'
            }), 500
            
    except Exception as e:
        print(f"Error generating insights: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate insights',
            'details': str(e)
        }), 500
    
if __name__ == '__main__':
    app.run(debug=True)