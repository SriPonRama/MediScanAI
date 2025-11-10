#!/usr/bin/env python3
"""
Test creating instances
"""

print("Testing instance creation...")

print("1. Testing ML model instance...")
try:
    from utils.ml_model import MLPredictor
    ml_predictor = MLPredictor()
    print("   ML model instance OK")
except Exception as e:
    print(f"   ML model instance FAILED: {e}")

print("2. Testing translator instance...")
try:
    from utils.translator import TranslationService
    translator = TranslationService()
    print("   Translator instance OK")
except Exception as e:
    print(f"   Translator instance FAILED: {e}")

print("3. Testing medical info instance...")
try:
    from utils.medical_info import MedicalInfoService
    medical_info = MedicalInfoService()
    print("   Medical info instance OK")
except Exception as e:
    print(f"   Medical info instance FAILED: {e}")

print("Test completed!")
