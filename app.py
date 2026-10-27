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
from models.database import db, User, Patient, Prediction, CheckupRecord, Notification, ChatMessage, init_db
from forms import (
    LoginForm, SignupForm, PatientForm, ImageUploadForm,
    CheckupRecordForm, PatientProfileForm, DoctorProfileForm, ChatMessageForm
)

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

# Initialize database with schema migrations
init_db(app)

# Initialize services
ml_predictor = EnhancedMLPredictor()
translator = TranslationService()
medical_info = MedicalInfoService()

@app.context_processor
def inject_translation():
    current_lang = session.get('lang', 'en')
    
    def _translate(text):
        if not text:
            return text
        return translator.translate_text(text, current_lang)
        
    unread_notifs = 0
    unread_msgs = 0
    if current_user.is_authenticated:
        try:
            unread_notifs = current_user.unread_notifications_count()
            unread_msgs = current_user.unread_messages_count()
        except Exception:
            pass
    
    return {
        'current_lang': current_lang,
        'current_lang_info': translator.supported_languages.get(current_lang, {'name': 'English', 'native': 'English', 'flag': '🌐'}),
        'supported_languages': translator.supported_languages,
        'unread_notifs': unread_notifs,
        'unread_msgs': unread_msgs,
        '_': _translate,
        't': _translate
    }

@app.template_filter('translate')
def translate_filter(text):
    current_lang = session.get('lang', 'en')
    return translator.translate_text(text, current_lang)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Landing page or direct portal routing"""
    if current_user.is_authenticated:
        if current_user.is_patient():
            return redirect(url_for('patient_portal'))
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/about')
def about():
    """About us page"""
    if current_user.is_authenticated:
        if current_user.is_patient():
            return redirect(url_for('patient_portal'))
        return redirect(url_for('dashboard'))
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with role-aware redirection"""
    if current_user.is_authenticated:
        if current_user.is_patient():
            return redirect(url_for('patient_portal'))
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.is_patient():
                return redirect(url_for('patient_portal'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration with Doctor and Patient portal support"""
    if current_user.is_authenticated:
        if current_user.is_patient():
            return redirect(url_for('patient_portal'))
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('auth/signup.html', form=form)
        
        role = form.role.data or 'doctor'
        hospital_name = form.hospital_name.data or 'MediScan Central Hospital'
        specialization = form.specialization.data or ('General Medicine' if role == 'doctor' else 'Patient')
        
        # Create new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            role=role,
            hospital_name=hospital_name,
            specialization=specialization
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        
        # If patient, link or create their clinical patient record
        if role == 'patient':
            # Check if doctor already created a patient record with this contact number
            existing_pat = Patient.query.filter_by(contact=form.phone.data).first()
            if existing_pat:
                user.patient_id = existing_pat.id
            else:
                # Create a baseline patient profile
                first_doc = User.query.filter_by(role='doctor').first()
                doc_id = first_doc.id if first_doc else 1
                new_pat = Patient(
                    user_id=doc_id,
                    name=form.name.data,
                    age=30,
                    gender='other',
                    contact=form.phone.data,
                    address='To be updated by patient'
                )
                db.session.add(new_pat)
                db.session.flush()
                user.patient_id = new_pat.id
                
            welcome_notif = Notification(
                user_id=user.id,
                title="Welcome to MediScan AI Patient Portal",
                message="Your personal health portal is active. You can review your medical checkups, vital signs, X-ray AI predictions, and securely communicate with doctors.",
                category='message',
                link=url_for('patient_portal')
            )
            db.session.add(welcome_notif)
            
        db.session.commit()
        
        flash(f'Account created successfully as {role.title()}! Please sign in.', 'success')
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
    """Doctor dashboard (redirects patient to patient portal)"""
    if current_user.is_patient():
        return redirect(url_for('patient_portal'))
        
    patients = Patient.query.filter_by(user_id=current_user.id).all()
    recent_predictions = []

    for patient in patients:
        patient_predictions = Prediction.query.filter_by(patient_id=patient.id).order_by(Prediction.created_at.desc()).limit(3).all()
        recent_predictions.extend(patient_predictions)

    recent_predictions.sort(key=lambda x: x.created_at, reverse=True)
    recent_predictions = recent_predictions[:5]

    recent_checkups = CheckupRecord.query.filter_by(doctor_id=current_user.id).order_by(CheckupRecord.visit_date.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           patients=patients, 
                           recent_predictions=recent_predictions,
                           recent_checkups=recent_checkups)

@app.route('/patient_portal')
@login_required
def patient_portal():
    """Dedicated Patient Portal for viewing checkups, vitals, AI predictions, and notifications"""
    if current_user.is_doctor():
        return redirect(url_for('dashboard'))
        
    # Find or link the patient record
    patient = current_user.patient_profile
    if not patient:
        patient = Patient.query.filter_by(contact=current_user.phone).first()
        if patient:
            current_user.patient_id = patient.id
            db.session.commit()
            
    if not patient:
        # Create default profile if not exists
        first_doc = User.query.filter_by(role='doctor').first()
        doc_id = first_doc.id if first_doc else 1
        patient = Patient(
            user_id=doc_id,
            name=current_user.name,
            contact=current_user.phone,
            age=30,
            gender='unspecified',
            address='To be updated'
        )
        db.session.add(patient)
        db.session.flush()
        current_user.patient_id = patient.id
        db.session.commit()

    predictions = Prediction.query.filter_by(patient_id=patient.id).order_by(Prediction.created_at.desc()).all()
    checkups = CheckupRecord.query.filter_by(patient_id=patient.id).order_by(CheckupRecord.visit_date.desc()).all()
    latest_checkup = checkups[0] if checkups else None
    
    # Identify doctor(s) associated with this patient
    doctor_ids = set()
    if patient.user_id:
        doctor_ids.add(patient.user_id)
    for c in checkups:
        if c.doctor_id:
            doctor_ids.add(c.doctor_id)
            
    doctors = User.query.filter(User.id.in_(doctor_ids)).all() if doctor_ids else User.query.filter_by(role='doctor').limit(3).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()

    return render_template('patient_portal.html',
                           patient=patient,
                           predictions=predictions,
                           checkups=checkups,
                           latest_checkup=latest_checkup,
                           doctors=doctors,
                           notifications=notifications)

@app.route('/patient_form', methods=['GET', 'POST'])
@login_required
def patient_form():
    """Add new patient (Doctors only)"""
    if current_user.is_patient():
        flash('Only medical practitioners can register new patients.', 'warning')
        return redirect(url_for('patient_portal'))
        
    form = PatientForm()

    if form.validate_on_submit():
        patient = Patient(
            user_id=current_user.id,
            name=form.name.data,
            dob=form.dob.data,
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
        
        # Link existing patient user account if matching phone
        matched_user = User.query.filter_by(phone=form.contact.data, role='patient').first()
        if matched_user:
            matched_user.patient_id = patient.id
            notif = Notification(
                user_id=matched_user.id,
                title="Medical Profile Connected",
                message=f"Dr. {current_user.name} at {current_user.hospital_name} has linked your patient record. All upcoming checkups and scans will be available here.",
                category='checkup',
                link=url_for('patient_portal')
            )
            db.session.add(notif)
            db.session.commit()

        flash(f'Patient "{patient.name}" created successfully! You can now record checkups or upload scans.', 'success')
        return redirect(url_for('patient_detail', patient_id=patient.id))

    return render_template('patient_form.html', form=form)

@app.route('/patient/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    """Doctor-only mutation of patient demographic & contact info"""
    if current_user.is_patient():
        flash('Patients cannot alter registered legal credentials. Contact your healthcare provider.', 'error')
        return redirect(url_for('patient_portal'))
        
    patient = Patient.query.get_or_404(patient_id)
    if patient.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
        
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.dob = form.dob.data
        patient.age = form.age.data
        patient.gender = form.gender.data
        patient.contact = form.contact.data
        patient.address = form.address.data
        patient.medical_history = form.medical_history.data
        patient.emergency_contact = form.emergency_contact.data
        patient.blood_group = form.blood_group.data
        patient.allergies = form.allergies.data
        
        db.session.commit()
        flash(f'Patient details for {patient.name} updated successfully!', 'success')
        return redirect(url_for('patient_detail', patient_id=patient.id))
        
    return render_template('patient_form.html', form=form, patient=patient, is_edit=True)

@app.route('/patient/<int:patient_id>/add_checkup', methods=['GET', 'POST'])
@app.route('/add_checkup', methods=['GET', 'POST'])
@login_required
def add_checkup(patient_id=None):
    """Add a hospital visit checkup record to a patient's permanent medical chart"""
    if current_user.is_patient():
        flash('Only healthcare professionals can record clinical checkup data.', 'warning')
        return redirect(url_for('patient_portal'))
        
    form = CheckupRecordForm()
    patients = Patient.query.filter_by(user_id=current_user.id).all()
    form.patient_id.choices = [(p.id, f"{p.name} (DOB: {p.dob or 'N/A'}, Age: {p.age}, ID: #{p.id})") for p in patients]
    
    if patient_id and request.method == 'GET':
        form.patient_id.data = patient_id

    if form.validate_on_submit():
        target_patient = Patient.query.get_or_404(form.patient_id.data)
        
        checkup = CheckupRecord(
            patient_id=target_patient.id,
            doctor_id=current_user.id,
            doctor_name=current_user.name,
            hospital_name=current_user.hospital_name or 'MediScan Central Hospital',
            visit_date=datetime.utcnow(),
            blood_pressure=form.blood_pressure.data,
            heart_rate=form.heart_rate.data,
            blood_sugar=form.blood_sugar.data,
            temperature=form.temperature.data,
            weight=form.weight.data,
            symptoms=form.symptoms.data,
            diagnosis=form.diagnosis.data,
            prescriptions=form.prescriptions.data,
            clinical_notes=form.clinical_notes.data,
            next_follow_up=form.next_follow_up.data
        )
        
        db.session.add(checkup)
        db.session.flush()
        
        # Send immediate notification to patient
        patient_user = target_patient.portal_user or User.query.filter_by(phone=target_patient.contact, role='patient').first()
        if patient_user:
            notif = Notification(
                user_id=patient_user.id,
                title=f"New Clinical Checkup Recorded by Dr. {current_user.name}",
                message=f"A new checkup record has been saved at {current_user.hospital_name}. Diagnosis: {form.diagnosis.data[:80]}. Prescriptions and vitals updated.",
                category='checkup',
                link=url_for('patient_portal')
            )
            db.session.add(notif)
            
        db.session.commit()
        flash(f'Checkup visit record saved for {target_patient.name} and shared with patient portal!', 'success')
        return redirect(url_for('patient_detail', patient_id=target_patient.id))
        
    return render_template('checkup_form.html', form=form, patients=patients, patient_id=patient_id)

@app.route('/upload_predict', methods=['GET', 'POST'])
@login_required
def upload_predict():
    """Upload X-ray and get prediction (Doctors only)"""
    if current_user.is_patient():
        flash('Only medical practitioners can submit clinical X-ray scans for AI analysis.', 'warning')
        return redirect(url_for('patient_portal'))
        
    form = ImageUploadForm()

    # Populate patient choices
    patients = Patient.query.filter_by(user_id=current_user.id).all()
    form.patient_id.choices = [(p.id, f"{p.name} (DOB: {p.dob or 'N/A'}, ID: #{p.id})") for p in patients]

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
            'doctor_notes': f'Clinical evaluation by Dr. {current_user.name} ({current_user.hospital_name}). AI Computer Vision Decision Support applied.'
        }

        # Save prediction to database (automatically transmitted to patient)
        prediction = Prediction(
            patient_id=form.patient_id.data,
            image_path=display_filename,
            body_part=body_part,
            prediction_result=prediction_result,
            confidence_score=confidence,
            additional_info=json.dumps(full_details),
            medical_tips=json.dumps(medical_info_data.get('medical_tips', [])),
            is_sent_to_patient=True
        )

        db.session.add(prediction)
        db.session.flush()

        # Send immediate notification to patient portal
        patient_user = patient.portal_user or User.query.filter_by(phone=patient.contact, role='patient').first()
        if patient_user:
            notif = Notification(
                user_id=patient_user.id,
                title=f"New X-ray Analysis: {prediction_result}",
                message=f"Dr. {current_user.name} uploaded and analyzed your {body_part.title()} X-ray. Finding: {prediction_result} ({round(confidence * 100, 1)}% confidence). View the full report in your portal.",
                category='report',
                link=url_for('view_prediction', prediction_id=prediction.id)
            )
            db.session.add(notif)

        db.session.commit()
        flash(f'X-ray analyzed successfully! Report generated and automatically sent to {patient.name}\'s portal.', 'success')

        return render_template('prediction_result.html',
                             prediction=prediction,
                             medical_info=full_details,
                             patient=patient)

    return render_template('upload_predict.html', form=form)

@app.route('/patient/<int:patient_id>')
@login_required
def patient_detail(patient_id):
    """View patient details, checkup history, and prediction history"""
    patient = Patient.query.get_or_404(patient_id)

    # Check authorization: Doctor who owns patient OR Patient who owns the profile
    is_authorized = (current_user.is_doctor() and patient.user_id == current_user.id) or \
                    (current_user.is_patient() and (current_user.patient_id == patient.id or current_user.phone == patient.contact))
                    
    if not is_authorized:
        flash('Access denied.', 'error')
        return redirect(url_for('patient_portal' if current_user.is_patient() else 'dashboard'))

    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(Prediction.created_at.desc()).all()
    checkups = CheckupRecord.query.filter_by(patient_id=patient_id).order_by(CheckupRecord.visit_date.desc()).all()

    return render_template('patient_detail.html', 
                           patient=patient, 
                           predictions=predictions,
                           checkups=checkups)


@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    """Switch active website language"""
    if lang_code in translator.supported_languages:
        session['lang'] = lang_code
    
    referrer = request.referrer
    if referrer and (request.host in referrer or referrer.startswith('/')):
        return redirect(referrer)
    return redirect(url_for('dashboard' if current_user.is_authenticated else 'index'))

@app.route('/translate', methods=['POST'])
@app.route('/api/translate', methods=['POST'], endpoint='api_translate')
def translate_text():
    """API endpoint for text translation (multilingual dynamic translation)"""
    data = request.get_json() or {}
    text = data.get('text', '')
    target_language = data.get('target_language', data.get('target_lang', session.get('lang', 'en')))
    source_language = data.get('source_lang', 'auto')

    if not text:
        return jsonify({'error': 'No text provided', 'translated_text': ''}), 400

    try:
        translated_text = translator.translate_text(text, target_language=target_language, source_language=source_language)
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'target_language': target_language,
            'target': target_language
        })
    except Exception as e:
        return jsonify({'error': str(e), 'translated_text': text}), 500


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

    # Dynamic localization of medical tips, description, and differential diagnosis
    current_lang = session.get('lang', 'en')
    if current_lang != 'en':
        display_info = dict(medical_info_data)
        if 'description' in display_info:
            display_info['description'] = translator.translate_text(display_info['description'], current_lang)
        if 'medical_tips' in display_info and isinstance(display_info['medical_tips'], list):
            display_info['medical_tips'] = [translator.translate_text(tip, current_lang) for tip in display_info['medical_tips']]
        if 'dietary_recommendations' in display_info and isinstance(display_info['dietary_recommendations'], list):
            display_info['dietary_recommendations'] = [translator.translate_text(tip, current_lang) for tip in display_info['dietary_recommendations']]
        if 'exercise_recommendations' in display_info and isinstance(display_info['exercise_recommendations'], list):
            display_info['exercise_recommendations'] = [translator.translate_text(tip, current_lang) for tip in display_info['exercise_recommendations']]
        if 'differential_diagnosis' in display_info and isinstance(display_info['differential_diagnosis'], list):
            translated_diff = []
            for item in display_info['differential_diagnosis']:
                it = dict(item)
                it['condition_translated'] = translator.translate_text(it.get('condition', ''), current_lang)
                translated_diff.append(it)
            display_info['differential_diagnosis'] = translated_diff
        medical_info_to_render = display_info
    else:
        medical_info_to_render = medical_info_data

    return render_template('prediction_result.html',
                         prediction=prediction,
                         medical_info=medical_info_to_render,
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

    current_lang = session.get('lang', 'en')
    if current_lang != 'en':
        display_info = dict(medical_info_data)
        if 'description' in display_info:
            display_info['description'] = translator.translate_text(display_info['description'], current_lang)
        if 'medical_tips' in display_info and isinstance(display_info['medical_tips'], list):
            display_info['medical_tips'] = [translator.translate_text(tip, current_lang) for tip in display_info['medical_tips']]
        if 'dietary_recommendations' in display_info and isinstance(display_info['dietary_recommendations'], list):
            display_info['dietary_recommendations'] = [translator.translate_text(tip, current_lang) for tip in display_info['dietary_recommendations']]
        if 'exercise_recommendations' in display_info and isinstance(display_info['exercise_recommendations'], list):
            display_info['exercise_recommendations'] = [translator.translate_text(tip, current_lang) for tip in display_info['exercise_recommendations']]
        medical_info_data = display_info

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


# ---------------------------------------------------------
# Profile Maintenance (Standard Clinical Practice Access Control)
# ---------------------------------------------------------
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Profile maintenance with role-specific constraints"""
    if current_user.is_doctor():
        form = DoctorProfileForm(obj=current_user)
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.phone = form.phone.data
            current_user.hospital_name = form.hospital_name.data
            current_user.specialization = form.specialization.data
            db.session.commit()
            flash('Professional profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        return render_template('profile.html', form=form, user=current_user, is_doctor=True)
    else:
        # Patient Profile: Name and Contact are strictly locked to protect legal/medical identity
        patient = current_user.patient_profile or Patient.query.filter_by(contact=current_user.phone).first()
        form = PatientProfileForm(obj=patient if patient else None)
        
        if form.validate_on_submit():
            if patient:
                patient.address = form.address.data
                patient.emergency_contact = form.emergency_contact.data
                patient.blood_group = form.blood_group.data
                patient.allergies = form.allergies.data
                patient.dob = form.dob.data
                db.session.commit()
                flash('Personal health profile updated successfully!', 'success')
                return redirect(url_for('profile'))
        
        return render_template('profile.html', 
                               form=form, 
                               user=current_user, 
                               patient=patient, 
                               is_doctor=False)


# ---------------------------------------------------------
# Doctor-Patient Multilingual Messaging System
# ---------------------------------------------------------
@app.route('/messages')
@login_required
def messages():
    """Messages inbox and contact selector"""
    contacts = []
    if current_user.is_doctor():
        # Doctor sees all their patients
        doctor_patients = Patient.query.filter_by(user_id=current_user.id).all()
        # Find any users linked to these patients
        for p in doctor_patients:
            pat_user = p.portal_user or User.query.filter_by(phone=p.contact, role='patient').first()
            if pat_user:
                unread = ChatMessage.query.filter_by(sender_id=pat_user.id, receiver_id=current_user.id, is_read=False).count()
                contacts.append({
                    'user': pat_user,
                    'patient': p,
                    'unread': unread
                })
    else:
        # Patient sees doctor(s) from their records
        patient = current_user.patient_profile or Patient.query.filter_by(contact=current_user.phone).first()
        doc_ids = set()
        if patient:
            if patient.user_id:
                doc_ids.add(patient.user_id)
            for ch in patient.checkups:
                if ch.doctor_id:
                    doc_ids.add(ch.doctor_id)
        if not doc_ids:
            doc_ids = [d.id for d in User.query.filter_by(role='doctor').limit(3).all()]
            
        for d_id in doc_ids:
            doc = User.query.get(d_id)
            if doc:
                unread = ChatMessage.query.filter_by(sender_id=doc.id, receiver_id=current_user.id, is_read=False).count()
                contacts.append({
                    'user': doc,
                    'patient': patient,
                    'unread': unread
                })

    selected_recipient = contacts[0]['user'] if contacts else None
    if selected_recipient:
        return redirect(url_for('chat_conversation', recipient_id=selected_recipient.id))
        
    return render_template('messages.html', contacts=contacts, active_chat=None, chat_messages=[])


@app.route('/messages/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def chat_conversation(recipient_id):
    """Direct conversation with auto-translation capabilities"""
    recipient = User.query.get_or_404(recipient_id)
    form = ChatMessageForm()
    
    # Mark incoming messages as read
    ChatMessage.query.filter_by(sender_id=recipient_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    if form.validate_on_submit() or (request.method == 'POST' and request.form.get('message')):
        msg_text = form.message.data or request.form.get('message', '').strip()
        if msg_text:
            chat_msg = ChatMessage(
                sender_id=current_user.id,
                receiver_id=recipient_id,
                message=msg_text,
                original_language=session.get('lang', 'en')
            )
            db.session.add(chat_msg)
            
            # Create in-app notification for recipient
            sender_role = "Dr. " + current_user.name if current_user.is_doctor() else current_user.name
            notif = Notification(
                user_id=recipient_id,
                title=f"New Message from {sender_role}",
                message=f"{msg_text[:90]}...",
                category='message',
                link=url_for('chat_conversation', recipient_id=current_user.id)
            )
            db.session.add(notif)
            db.session.commit()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message_id': chat_msg.id})
                
            return redirect(url_for('chat_conversation', recipient_id=recipient_id))

    # Fetch conversation thread
    thread = ChatMessage.query.filter(
        ((ChatMessage.sender_id == current_user.id) & (ChatMessage.receiver_id == recipient_id)) |
        ((ChatMessage.sender_id == recipient_id) & (ChatMessage.receiver_id == current_user.id))
    ).order_by(ChatMessage.created_at.asc()).all()

    # Build contacts list for sidebar
    contacts = []
    if current_user.is_doctor():
        doctor_patients = Patient.query.filter_by(user_id=current_user.id).all()
        for p in doctor_patients:
            pat_user = p.portal_user or User.query.filter_by(phone=p.contact, role='patient').first()
            if pat_user:
                unread = ChatMessage.query.filter_by(sender_id=pat_user.id, receiver_id=current_user.id, is_read=False).count()
                contacts.append({'user': pat_user, 'patient': p, 'unread': unread})
    else:
        patient = current_user.patient_profile or Patient.query.filter_by(contact=current_user.phone).first()
        doc_ids = set()
        if patient:
            if patient.user_id:
                doc_ids.add(patient.user_id)
            for ch in patient.checkups:
                if ch.doctor_id:
                    doc_ids.add(ch.doctor_id)
        if not doc_ids:
            doc_ids = [d.id for d in User.query.filter_by(role='doctor').limit(3).all()]
        for d_id in doc_ids:
            doc = User.query.get(d_id)
            if doc:
                unread = ChatMessage.query.filter_by(sender_id=doc.id, receiver_id=current_user.id, is_read=False).count()
                contacts.append({'user': doc, 'patient': patient, 'unread': unread})

    return render_template('messages.html', 
                           contacts=contacts, 
                           active_chat=recipient, 
                           chat_messages=thread, 
                           form=form)


# ---------------------------------------------------------
# In-App Notifications
# ---------------------------------------------------------
@app.route('/notifications')
@login_required
def notifications():
    """List all in-app notifications and mark as read"""
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark all as read
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('notifications.html', notifications=notifs)


@app.route('/notifications/read/<int:notif_id>')
@login_required
def read_notification(notif_id):
    """Mark a single notification as read and route to its target"""
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id == current_user.id:
        notif.is_read = True
        db.session.commit()
        if notif.link:
            return redirect(notif.link)
    return redirect(url_for('notifications'))


# ---------------------------------------------------------
# Immutability Guard for Generated Medical Predictions & Records
# ---------------------------------------------------------
@app.route('/prediction/<int:prediction_id>/delete', methods=['GET', 'POST'])
@app.route('/patient/<int:patient_id>/delete', methods=['GET', 'POST'])
@login_required
def block_deletion(prediction_id=None, patient_id=None):
    """Enforce clinical audit trail: finalized predictions cannot be erased"""
    flash('Permanent Audit Trail Enforced: Clinical X-ray predictions and validated diagnostic reports cannot be deleted once transmitted to patient charts.', 'error')
    if current_user.is_patient():
        return redirect(url_for('patient_portal'))
    return redirect(url_for('dashboard'))



if __name__ == '__main__':
    print("Starting MediScan AI...")
    print("Visit: http://localhost:5000")
    print("Demo login: demo@mediscan.com / demo123")
    app.run(debug=True, host='0.0.0.0', port=5000)
