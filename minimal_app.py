#!/usr/bin/env python3
"""
Minimal Flask app to test basic functionality
"""

import os
import secrets
from flask import Flask, render_template, redirect, url_for, flash
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mediscan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About us page"""
    return render_template('about.html')

@app.route('/login')
def login():
    """Login page"""
    return "<h1>Login Page</h1><p>This is a minimal test. <a href='/'>Go back to home</a></p>"

@app.route('/signup')
def signup():
    """Signup page"""
    return "<h1>Signup Page</h1><p>This is a minimal test. <a href='/'>Go back to home</a></p>"

if __name__ == '__main__':
    print("Starting MediScan AI minimal app...")
    print("Visit: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
