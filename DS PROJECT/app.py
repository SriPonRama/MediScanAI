import os
import secrets
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import models and forms
from models.database import db, User, Patient, Prediction
from forms import LoginForm, SignupForm, PatientForm, ImageUploadForm

# Import ML and translation utilities
from utils.enhanced_ml_model import EnhancedMLPredictor
from utils.translator import TranslationService
from utils.medical_info import MedicalInfoService

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mediscan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize database (only create tables, don't recreate)
db.init_app(app)
with app.app_context():
    db.create_all()

# Initialize services
ml_predictor = EnhancedMLPredictor()
translator = TranslationService()
medical_info = MedicalInfoService()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About us page"""
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('auth/signup.html', form=form)
        
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    patients = Patient.query.filter_by(user_id=current_user.id).all()
    recent_predictions = []

    for patient in patients:
        patient_predictions = Prediction.query.filter_by(patient_id=patient.id).order_by(Prediction.created_at.desc()).limit(3).all()
        recent_predictions.extend(patient_predictions)

    recent_predictions.sort(key=lambda x: x.created_at, reverse=True)
    recent_predictions = recent_predictions[:5]  # Show only 5 most recent

    return render_template('dashboard.html', patients=patients, recent_predictions=recent_predictions)

@app.route('/patient_form', methods=['GET', 'POST'])
@login_required
def patient_form():
    """Add/Edit patient information"""
    form = PatientForm()

    if form.validate_on_submit():
        patient = Patient(
            user_id=current_user.id,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            contact=form.contact.data,
            address=form.address.data,
            medical_history=form.medical_history.data,
            emergency_contact=form.emergency_contact.data,
            blood_group=form.blood_group.data,
            allergies=form.allergies.data
        )

        db.session.add(patient)
        db.session.commit()

        flash('Patient information saved successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('patient_form.html', form=form)

@app.route('/upload_predict', methods=['GET', 'POST'])
@login_required
def upload_predict():
    """Upload X-ray and get prediction"""
    form = ImageUploadForm()

    # Populate patient choices
    patients = Patient.query.filter_by(user_id=current_user.id).all()
    form.patient_id.choices = [(p.id, p.name) for p in patients]

    if not patients:
        flash('Please add a patient first before uploading X-rays.', 'warning')
        return redirect(url_for('patient_form'))

    if form.validate_on_submit():
        # Save uploaded file
        file = form.image.data
        filename = secure_filename(file.filename)
        timestamp = str(int(time.time()))
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Get patient information for better prediction
        patient = Patient.query.get(form.patient_id.data)
        body_part = form.body_part.data

        # Get enhanced prediction with patient context
        prediction_result, confidence = ml_predictor.predict(
            file_path, body_part,
            patient_age=patient.age,
            patient_gender=patient.gender
        )

        # Get medical information
        medical_info_data = medical_info.get_medical_info(prediction_result)

        # Save prediction to database
        prediction = Prediction(
            patient_id=form.patient_id.data,
            image_path=filename,
            body_part=body_part,
            prediction_result=prediction_result,
            confidence_score=confidence,
            additional_info=json.dumps(medical_info_data),
            medical_tips=json.dumps(medical_info_data.get('medical_tips', []))
        )

        db.session.add(prediction)
        db.session.commit()

        return render_template('prediction_result.html',
                             prediction=prediction,
                             medical_info=medical_info_data,
                             patient=Patient.query.get(form.patient_id.data))

    return render_template('upload_predict.html', form=form)

@app.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """View patient details and prediction history"""
    patient = Patient.query.get_or_404(patient_id)

    # Check if patient belongs to current user
    if patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).all()

    return render_template('patient_detail.html', patient=patient, predictions=predictions)

@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    """API endpoint for text translation"""
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('target_language', 'en')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        translated_text = translator.translate_text(text, target_language)
        return jsonify({'translated_text': translated_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/model_info/<body_part>')
@login_required
def get_model_info(body_part):
    """Get ML model information for a body part"""
    try:
        model_info = ml_predictor.get_model_info(body_part)
        if model_info:
            return jsonify({
                'body_part': body_part,
                'model_info': model_info,
                'supported_conditions': ml_predictor.get_possible_conditions(body_part)
            })
        else:
            return jsonify({'error': 'Body part not supported'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supported_body_parts')
@login_required
def get_supported_body_parts():
    """Get list of supported body parts"""
    try:
        body_parts = ml_predictor.get_supported_body_parts()
        return jsonify({'supported_body_parts': body_parts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/prediction/<int:prediction_id>')
@login_required
def view_prediction(prediction_id):
    """View detailed prediction results"""
    prediction = Prediction.query.get_or_404(prediction_id)

    # Check if prediction belongs to current user's patient
    if prediction.patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    # Get medical information
    try:
        medical_info_data = json.loads(prediction.additional_info) if prediction.additional_info else {}
    except:
        medical_info_data = medical_info.get_medical_info(prediction.prediction_result)

    return render_template('prediction_result.html',
                         prediction=prediction,
                         medical_info=medical_info_data,
                         patient=prediction.patient)

if __name__ == '__main__':
    print("Starting MediScan AI...")
    print("Visit: http://localhost:5000")
    print("Demo login: demo@mediscan.com / demo123")
    app.run(debug=True, host='0.0.0.0', port=5000)
