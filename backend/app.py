import os
import smtplib
from email.message import EmailMessage
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
import random, string

# --- Configuration (configure your email here) ---
EMAIL_ADDRESS = 'teasporch@gmail.com'  # আপনার ইমেইল
EMAIL_PASSWORD = '@Ahad@696##'    # আপনার ইমেইলের পাসওয়ার্ড

# --- Flask App Setup ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

app = Flask(
    __name__,
    template_folder=os.path.join(PROJECT_DIR, 'frontend', 'templates'),
    static_folder=os.path.join(PROJECT_DIR, 'frontend', 'static')
)

db_path = os.path.join(PROJECT_DIR, 'database', 'db.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'your_strong_and_unique_secret_key_here'

db.init_app(app)

# --- Email Sender Function ---
def send_welcome_email(recipient_email, user_name):
    try:
        msg = EmailMessage()
        msg['Subject'] = 'Welcome to Our Website!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient_email
        msg.set_content(f"""
        Hello {user_name},

        Welcome to our website! We're glad to have you with us.
        You can now explore all our features.

        Best regards,
        The Team
        """)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print(f"Failed to send email: {e}")

# --- Routes ---
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Simulate a delay for loading effect
        import time
        time.sleep(2) 

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'This email is already registered!'})

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        new_user = User(name=name, email=email, password=hashed_password, referral_code=code)
        db.session.add(new_user)
        db.session.commit()
        
        # Send welcome email (optional)
        # send_welcome_email(email, name)
        
        return jsonify({'success': True, 'message': 'Registration successful!'})

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Simulate a delay for loading effect
        import time
        time.sleep(2) 

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['email'] = user.email
            return jsonify({'success': True, 'message': 'Login successful!'})
        else:
            return jsonify({'success': False, 'message': 'Incorrect email or password.'})

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(email=session['email']).first()
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
