#!/usr/bin/env python3
"""
Test models import
"""

print("Testing models import...")

print("1. Testing database models import...")
try:
    from models.database import db, User, Patient, Prediction
    print("   Models import OK")
except Exception as e:
    print(f"   Models import FAILED: {e}")

print("Test completed!")
