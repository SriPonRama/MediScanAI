from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='doctor', nullable=False)  # 'doctor' or 'patient'
    hospital_name = db.Column(db.String(150), default='MediScan Central Hospital', nullable=True)
    specialization = db.Column(db.String(100), default='Radiology & General Medicine', nullable=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patients = db.relationship('Patient', backref='user', foreign_keys='Patient.user_id', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', foreign_keys='Notification.user_id', lazy=True, cascade='all, delete-orphan', order_by='Notification.created_at.desc()')
    sent_messages = db.relationship('ChatMessage', backref='sender', foreign_keys='ChatMessage.sender_id', lazy=True)
    received_messages = db.relationship('ChatMessage', backref='receiver', foreign_keys='ChatMessage.receiver_id', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_doctor(self):
        return self.role == 'doctor'
        
    def is_patient(self):
        return self.role == 'patient'
        
    def unread_notifications_count(self):
        return Notification.query.filter_by(user_id=self.id, is_read=False).count()
        
    def unread_messages_count(self):
        return ChatMessage.query.filter_by(receiver_id=self.id, is_read=False).count()
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    dob = db.Column(db.String(20), nullable=True)  # YYYY-MM-DD
    address = db.Column(db.Text, nullable=True)
    medical_history = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String(20), nullable=True)
    blood_group = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='patient', lazy=True, cascade='all, delete-orphan', order_by='Prediction.created_at.desc()')
    checkups = db.relationship('CheckupRecord', backref='patient', lazy=True, cascade='all, delete-orphan', order_by='CheckupRecord.visit_date.desc()')
    portal_user = db.relationship('User', backref='patient_profile', foreign_keys='User.patient_id', uselist=False)
    
    def __repr__(self):
        return f'<Patient {self.name}>'

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)
    prediction_result = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    medical_tips = db.Column(db.Text, nullable=True)
    is_sent_to_patient = db.Column(db.Boolean, default=True)  # Automatically shared with patient
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.prediction_result} - {self.confidence_score:.2f}>'

class CheckupRecord(db.Model):
    __tablename__ = 'checkup_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Clinical Vitals
    blood_pressure = db.Column(db.String(30), nullable=True)  # e.g., "120/80 mmHg"
    heart_rate = db.Column(db.String(30), nullable=True)      # e.g., "72 bpm"
    blood_sugar = db.Column(db.String(30), nullable=True)     # e.g., "95 mg/dL"
    temperature = db.Column(db.String(30), nullable=True)     # e.g., "98.6 °F"
    weight = db.Column(db.String(30), nullable=True)          # e.g., "68 kg"
    
    # Clinical notes & prescriptions
    symptoms = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    prescriptions = db.Column(db.Text, nullable=True)
    clinical_notes = db.Column(db.Text, nullable=True)
    next_follow_up = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    
    def __repr__(self):
        return f'<CheckupRecord Patient={self.patient_id} Date={self.visit_date}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='report')  # 'report', 'checkup', 'message'
    link = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.title} for User={self.user_id}>'

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    original_language = db.Column(db.String(20), default='auto')
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage from {self.sender_id} to {self.receiver_id}>'

def init_db(app):
    """Initialize database with app context and apply lightweight migrations"""
    db.init_app(app)
    
    with app.app_context():
        # First ensure all base tables are created
        db.create_all()
        
        # Check and migrate columns dynamically if they don't exist yet
        try:
            with db.engine.connect() as conn:
                # 1. Check users table columns
                res = conn.execute(db.text("PRAGMA table_info(users)")).fetchall()
                col_names = [r[1] for r in res]
                if 'role' not in col_names:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'doctor'"))
                if 'hospital_name' not in col_names:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN hospital_name VARCHAR(150) DEFAULT 'MediScan Central Hospital'"))
                if 'specialization' not in col_names:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN specialization VARCHAR(100) DEFAULT 'Radiology & General Medicine'"))
                if 'patient_id' not in col_names:
                    conn.execute(db.text("ALTER TABLE users ADD COLUMN patient_id INTEGER"))
                
                # 2. Check patients table columns
                res_pat = conn.execute(db.text("PRAGMA table_info(patients)")).fetchall()
                pat_cols = [r[1] for r in res_pat]
                if 'dob' not in pat_cols:
                    conn.execute(db.text("ALTER TABLE patients ADD COLUMN dob VARCHAR(20)"))
                
                # 3. Check predictions table columns
                res_pred = conn.execute(db.text("PRAGMA table_info(predictions)")).fetchall()
                pred_cols = [r[1] for r in res_pred]
                if 'is_sent_to_patient' not in pred_cols:
                    conn.execute(db.text("ALTER TABLE predictions ADD COLUMN is_sent_to_patient BOOLEAN DEFAULT 1"))
                    
                conn.commit()
        except Exception as e:
            print(f"Database migration note: {e}")
            
        print("Database initialized and verified successfully!")

