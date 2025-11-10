#!/usr/bin/env python3
"""
Test utils import
"""

print("Testing utils import...")

print("1. Testing ML model import...")
try:
    from utils.ml_model import MLPredictor
    print("   ML model import OK")
except Exception as e:
    print(f"   ML model import FAILED: {e}")

print("2. Testing translator import...")
try:
    from utils.translator import TranslationService
    print("   Translator import OK")
except Exception as e:
    print(f"   Translator import FAILED: {e}")

print("3. Testing medical info import...")
try:
    from utils.medical_info import MedicalInfoService
    print("   Medical info import OK")
except Exception as e:
    print(f"   Medical info import FAILED: {e}")

print("Test completed!")
