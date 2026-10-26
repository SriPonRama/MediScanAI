import os
import secrets
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import models and forms
from models.database import db, User, Patient, Prediction
from forms import LoginForm, SignupForm, PatientForm, ImageUploadForm

# Import ML, translation, and report utilities
from utils.enhanced_ml_model import EnhancedMLPredictor
try:
    from utils.translator import TranslationService
except ImportError:
    from utils.translator_fallback import TranslationService
from utils.medical_info import MedicalInfoService
from utils.report_generator import generate_radiology_pdf

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

        # Handle DICOM or standard image
        is_dcm = filename.lower().endswith('.dcm')
        display_filename = filename
        dcm_meta = None

        if is_dcm:
            preview_filename, dcm_meta = ml_predictor.process_dicom(file_path, app.config['UPLOAD_FOLDER'])
            if preview_filename:
                display_filename = preview_filename

        # Get enhanced prediction with patient context
        prediction_result, confidence, analysis_details = ml_predictor.predict(
            file_path, body_part,
            patient_age=patient.age,
            patient_gender=patient.gender
        )

        # Get medical information
        medical_info_data = medical_info.get_medical_info(prediction_result)

        full_details = {
            **medical_info_data,
            **analysis_details,
            'display_image': display_filename,
            'is_dicom': is_dcm,
            'dicom_metadata': dcm_meta,
            'doctor_notes': 'Clinical correlation recommended. Evaluated via AI Decision Support.'
        }

        # Save prediction to database
        prediction = Prediction(
            patient_id=form.patient_id.data,
            image_path=display_filename,
            body_part=body_part,
            prediction_result=prediction_result,
            confidence_score=confidence,
            additional_info=json.dumps(full_details),
            medical_tips=json.dumps(medical_info_data.get('medical_tips', []))
        )

        db.session.add(prediction)
        db.session.commit()

        return render_template('prediction_result.html',
                             prediction=prediction,
                             medical_info=full_details,
                             patient=patient)

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
        # Use local translations for common medical terms
        local_translations = {
            'hi': {
                'Normal': 'सामान्य',
                'Pneumonia': 'निमोनिया',
                'COVID-19': 'कोविड-19',
                'Fracture': 'हड्डी टूटना',
                'Arthritis': 'गठिया',
                'Tuberculosis': 'तपेदिक',
                'Lung Cancer': 'फेफड़ों का कैंसर',
                'Dislocation': 'हड्डी का खिसकना',
                'Bone Tumor': 'हड्डी का ट्यूमर'
            },
            'ta': {
                'Normal': 'சாதாரண',
                'Pneumonia': 'நுரையீரல் அழற்சி',
                'COVID-19': 'கோவிட்-19',
                'Fracture': 'எலும்பு முறிவு',
                'Arthritis': 'மூட்டு வலி',
                'Tuberculosis': 'காசநோய்',
                'Lung Cancer': 'நுரையீரல் புற்றுநோய்',
                'Dislocation': 'எலும்பு இடப்பெயர்வு',
                'Bone Tumor': 'எலும்பு கட்டி'
            },
            'te': {
                'Normal': 'సాధారణ',
                'Pneumonia': 'న్యుమోనియా',
                'COVID-19': 'కోవిడ్-19',
                'Fracture': 'ఎముక విరుపు',
                'Arthritis': 'కీళ్ల వాపు',
                'Tuberculosis': 'క్షయవ్యాధి',
                'Lung Cancer': 'ఊపిరితిత్తుల క్యాన్సర్',
                'Dislocation': 'ఎముక స్థానభ్రంశం',
                'Bone Tumor': 'ఎముక కణితి'
            },
            'bn': {
                'Normal': 'স্বাভাবিক',
                'Pneumonia': 'নিউমোনিয়া',
                'COVID-19': 'কোভিড-১৯',
                'Fracture': 'হাড় ভাঙা',
                'Arthritis': 'বাত',
                'Tuberculosis': 'যক্ষ্মা',
                'Lung Cancer': 'ফুসফুসের ক্যান্সার',
                'Dislocation': 'হাড়ের স্থানচ্যুতি',
                'Bone Tumor': 'হাড়ের টিউমার'
            }
        }
        
        if target_language in local_translations and text in local_translations[target_language]:
            translated_text = local_translations[target_language][text]
        else:
            # Fallback to original text if no translation available
            translated_text = text
            
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
    except Exception:
        medical_info_data = {}

    if not medical_info_data or 'description' not in medical_info_data:
        fallback_data = medical_info.get_medical_info(prediction.prediction_result)
        medical_info_data.update(fallback_data)

    # Backwards compatibility: If differential diagnosis or heatmap is missing for an older prediction, generate on the fly
    if 'differential_diagnosis' not in medical_info_data:
        upload_folder = app.config['UPLOAD_FOLDER']
        img_full_path = os.path.join(upload_folder, prediction.image_path)
        if os.path.exists(img_full_path):
            try:
                _, _, details = ml_predictor.predict(img_full_path, prediction.body_part, prediction.patient.age, prediction.patient.gender)
                medical_info_data.update(details)
                prediction.additional_info = json.dumps(medical_info_data)
                db.session.commit()
            except Exception as e:
                print(f"Error generating on-the-fly details: {e}")

    return render_template('prediction_result.html',
                         prediction=prediction,
                         medical_info=medical_info_data,
                         patient=prediction.patient)

@app.route('/prediction/<int:prediction_id>/download_report')
@login_required
def download_radiology_report(prediction_id):
    """Generate and download clinical PDF radiology report"""
    prediction = Prediction.query.get_or_404(prediction_id)

    if prediction.patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    try:
        doctor_name = f"Dr. {current_user.name}"
        pdf_buffer = generate_radiology_pdf(prediction, prediction.patient, doctor_name)
        safe_name = secure_filename(prediction.patient.name).replace(' ', '_')
        report_filename = f"MediScan_Report_{safe_name}_{prediction.id}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Error generating PDF report: {e}", 'error')
        return redirect(url_for('view_prediction', prediction_id=prediction.id))

@app.route('/prediction/<int:prediction_id>/print_report')
@app.route('/prediction/<int:prediction_id>/print')
@login_required
def print_radiology_report(prediction_id):
    """View print-ready formatted clinical radiology report"""
    prediction = Prediction.query.get_or_404(prediction_id)

    if prediction.patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    try:
        medical_info_data = json.loads(prediction.additional_info) if prediction.additional_info else {}
    except Exception:
        medical_info_data = {}

    return render_template('print_report.html',
                         prediction=prediction,
                         medical_info=medical_info_data,
                         patient=prediction.patient,
                         doctor_name=current_user.name)

@app.route('/prediction/<int:prediction_id>/save_notes', methods=['POST'])
@login_required
def save_doctor_notes(prediction_id):
    """Save radiologist / doctor dictated impressions & clinical notes"""
    prediction = Prediction.query.get_or_404(prediction_id)

    if prediction.patient.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    notes = data.get('notes', '').strip()

    try:
        info_data = json.loads(prediction.additional_info) if prediction.additional_info else {}
        info_data['doctor_notes'] = notes
        prediction.additional_info = json.dumps(info_data)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Clinical notes saved successfully.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/patient/<int:patient_id>/compare')
@login_required
def patient_compare(patient_id):
    """Longitudinal timeline scan comparison and healing response tracking"""
    patient = Patient.query.get_or_404(patient_id)

    if patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))

    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.asc()).all()
    if len(predictions) < 2:
        flash('At least 2 scans are required to perform longitudinal comparison.', 'warning')
        return redirect(url_for('patient_detail', patient_id=patient.id))

    scan1_id = request.args.get('scan1', type=int) or predictions[0].id
    scan2_id = request.args.get('scan2', type=int) or predictions[-1].id

    scan1 = Prediction.query.get_or_404(scan1_id)
    scan2 = Prediction.query.get_or_404(scan2_id)

    # Compute delta metrics
    try:
        scan1_info = json.loads(scan1.additional_info) if scan1.additional_info else {}
    except Exception:
        scan1_info = {}

    try:
        scan2_info = json.loads(scan2.additional_info) if scan2.additional_info else {}
    except Exception:
        scan2_info = {}

    days_elapsed = abs((scan2.created_at - scan1.created_at).days)
    conf_delta = round((scan2.confidence_score - scan1.confidence_score) * 100, 1)

    density1 = scan1_info.get('abnormality_density_pct', 20.0)
    density2 = scan2_info.get('abnormality_density_pct', 20.0)
    density_delta = round(density2 - density1, 1)

    # Clinical progression determination
    if scan2.prediction_result == 'Normal' and scan1.prediction_result != 'Normal':
        progression_status = 'Resolved / Complete Remission'
        progression_badge = 'success'
        progression_summary = 'Significant anatomical clearing observed. Active pathological infiltration resolved.'
    elif density_delta < -5.0:
        progression_status = 'Positive Therapeutic Response (Regression)'
        progression_badge = 'success'
        progression_summary = f'Abnormality density decreased by {abs(density_delta)}%. Favorable therapeutic response noted.'
    elif density_delta > 5.0 or (scan2.prediction_result != 'Normal' and scan1.prediction_result == 'Normal'):
        progression_status = 'Pathology Progression / Increased Infiltration'
        progression_badge = 'danger'
        progression_summary = f'Abnormality density increased by {density_delta}%. Close clinical correlation warranted.'
    else:
        progression_status = 'Stationary / Stable Lesion'
        progression_badge = 'info'
        progression_summary = 'No significant change in morphological features between scan dates.'

    return render_template('patient_compare.html',
                         patient=patient,
                         predictions=predictions,
                         scan1=scan1,
                         scan2=scan2,
                         scan1_info=scan1_info,
                         scan2_info=scan2_info,
                         days_elapsed=days_elapsed,
                         conf_delta=conf_delta,
                         density_delta=density_delta,
                         progression_status=progression_status,
                         progression_badge=progression_badge,
                         progression_summary=progression_summary)


if __name__ == '__main__':
    print("Starting MediScan AI...")
    print("Visit: http://localhost:5000")
    print("Demo login: demo@mediscan.com / demo123")
    app.run(debug=True, host='0.0.0.0', port=5000)
