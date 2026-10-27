from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    role = SelectField('Register As', choices=[
        ('doctor', 'Doctor / Medical Practitioner'),
        ('patient', 'Patient / Personal Healthcare')
    ], default='doctor', validators=[DataRequired()])
    hospital_name = StringField('Hospital / Clinic Name (Optional for Doctors)', validators=[Optional(), Length(max=150)])
    specialization = StringField('Medical Specialty (Optional for Doctors)', validators=[Optional(), Length(max=100)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

class PatientForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired(), Length(min=2, max=100)])
    dob = StringField('Date of Birth (YYYY-MM-DD)', validators=[Optional(), Length(max=20)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    contact = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Address', validators=[Optional()])
    medical_history = TextAreaField('Medical History', validators=[Optional()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=20)])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    allergies = TextAreaField('Known Allergies', validators=[Optional()])
    submit = SubmitField('Save Patient Information')

class CheckupRecordForm(FlaskForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    blood_pressure = StringField('Blood Pressure (e.g. 120/80 mmHg)', validators=[Optional(), Length(max=30)])
    heart_rate = StringField('Heart Rate (e.g. 72 bpm)', validators=[Optional(), Length(max=30)])
    blood_sugar = StringField('Blood Sugar / Glucose (e.g. 95 mg/dL)', validators=[Optional(), Length(max=30)])
    temperature = StringField('Body Temperature (e.g. 98.6 °F)', validators=[Optional(), Length(max=30)])
    weight = StringField('Body Weight (e.g. 68 kg)', validators=[Optional(), Length(max=30)])
    symptoms = TextAreaField('Patient Symptoms & Chief Complaints', validators=[Optional()])
    diagnosis = TextAreaField('Doctor Clinical Assessment & Findings', validators=[DataRequired()])
    prescriptions = TextAreaField('Prescribed Medicines, Dosages & Routine', validators=[Optional()])
    clinical_notes = TextAreaField('Clinical Recommendations & Dietary Advice', validators=[Optional()])
    next_follow_up = StringField('Next Recommended Checkup Date', validators=[Optional(), Length(max=50)])
    submit = SubmitField('Save & Send Checkup Record to Patient')

class PatientProfileForm(FlaskForm):
    # Name and Contact are controlled and locked for patients as requested
    address = TextAreaField('Residential Address', validators=[Optional()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional(), Length(max=20)])
    blood_group = SelectField('Blood Group', choices=[
        ('', 'Select Blood Group'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], validators=[Optional()])
    allergies = TextAreaField('Known Allergies', validators=[Optional()])
    dob = StringField('Date of Birth (YYYY-MM-DD)', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Update Profile')

class DoctorProfileForm(FlaskForm):
    name = StringField('Doctor Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Contact Number', validators=[DataRequired(), Length(min=10, max=20)])
    hospital_name = StringField('Hospital / Affiliation', validators=[Optional(), Length(max=150)])
    specialization = StringField('Medical Specialty', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Update Professional Profile')

class ChatMessageForm(FlaskForm):
    receiver_id = IntegerField('Recipient ID', validators=[DataRequired()])
    message = TextAreaField('Type your message or medical query...', validators=[DataRequired(), Length(min=1, max=3000)])
    submit = SubmitField('Send Message')

class ImageUploadForm(FlaskForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    image = FileField('X-ray Image / DICOM Scan', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'dcm'], 'Only JPG, JPEG, PNG, and DICOM (.dcm) files are allowed!')
    ])
    body_part = SelectField('Body Part', choices=[
        ('chest', 'Chest'),
        ('hand', 'Hand'),
        ('leg', 'Leg'),
        ('skull', 'Skull'),
        ('spine', 'Spine'),
        ('pelvis', 'Pelvis')
    ], validators=[DataRequired()])
    submit = SubmitField('Upload and Analyze')

