#!/usr/bin/env python3
"""
Test imports step by step
"""

print("Testing imports...")

print("1. Testing basic imports...")
import os
import sys
print("   Basic imports OK")

print("2. Testing Flask import...")
from flask import Flask
print("   Flask import OK")

print("3. Testing dotenv import...")
from dotenv import load_dotenv
print("   dotenv import OK")

print("4. Loading environment...")
load_dotenv()
print("   Environment loaded OK")

print("5. Creating Flask app...")
app = Flask(__name__)
print("   Flask app created OK")

print("All imports successful!")
print("If you see database initialization messages, the issue is elsewhere.")
