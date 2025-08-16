#!/usr/bin/env python3
"""
Test app import step by step
"""

print("Testing app import...")

print("1. Testing basic Flask setup...")
import os
import secrets
import time
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json
print("   Basic imports OK")

print("2. Loading environment...")
load_dotenv()
print("   Environment loaded OK")

print("3. Testing models import...")
from models.database import db, User, Patient, Prediction
print("   Models imported OK")

print("4. Testing forms import...")
from forms import LoginForm, SignupForm, PatientForm, ImageUploadForm
print("   Forms imported OK")

print("5. Testing utils imports...")
from utils.ml_model import MLPredictor
from utils.translator import TranslationService
from utils.medical_info import MedicalInfoService
print("   Utils imported OK")

print("6. Creating Flask app...")
app = Flask(__name__)
print("   Flask app created OK")

print("7. Configuring app...")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mediscan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
print("   App configured OK")

print("8. Initializing extensions...")
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
print("   Extensions initialized OK")

print("9. Initializing database...")
db.init_app(app)
with app.app_context():
    db.create_all()
print("   Database initialized OK")

print("10. Creating service instances...")
ml_predictor = MLPredictor()
translator = TranslationService()
medical_info = MedicalInfoService()
print("   Services created OK")

print("All steps completed successfully!")
print("If you see database initialization messages, they're coming from somewhere else.")
