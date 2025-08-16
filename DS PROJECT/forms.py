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

class ImageUploadForm(FlaskForm):
    patient_id = SelectField('Select Patient', coerce=int, validators=[DataRequired()])
    image = FileField('X-ray Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only JPG, JPEG, and PNG images are allowed!')
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
