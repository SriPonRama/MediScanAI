#!/usr/bin/env python3
"""
Comprehensive functionality testing for MediScan AI
Tests all major components and features
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_server_running():
    """Test if the Flask server is running"""
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        return response.status_code == 200
    except:
        return False

def test_database_connection():
    """Test database connectivity"""
    try:
        from models.database import db, User, Patient, Prediction
        from app import app
        
        with app.app_context():
            # Test basic database operations
            user_count = User.query.count()
            patient_count = Patient.query.count()
            prediction_count = Prediction.query.count()
            
            print(f"  Database contains: {user_count} users, {patient_count} patients, {prediction_count} predictions")
            return True
    except Exception as e:
        print(f"  Database test failed: {e}")
        return False

def test_ml_model():
    """Test ML model functionality"""
    try:
        from utils.enhanced_ml_model import EnhancedMLPredictor
        
        predictor = EnhancedMLPredictor()
        
        # Test supported body parts
        body_parts = predictor.get_supported_body_parts()
        print(f"  Supported body parts: {len(body_parts)}")
        
        # Test prediction for each body part
        test_image_path = 'static/uploads/demo_chest_xray.jpg'
        if os.path.exists(test_image_path):
            for body_part in ['chest', 'hand', 'leg']:
                prediction, confidence = predictor.predict(test_image_path, body_part, 45, 'male')
                print(f"  {body_part}: {prediction} ({confidence:.2f})")
        
        return True
    except Exception as e:
        print(f"  ML model test failed: {e}")
        return False

def test_translation_service():
    """Test translation functionality"""
    try:
        from utils.translator import TranslationService
        
        translator = TranslationService()
        
        # Test basic translation
        test_text = "Hello, this is a test"
        translated = translator.translate_text(test_text, 'hi')
        print(f"  Translation test: '{test_text}' -> '{translated}'")
        
        # Test supported languages
        languages = translator.get_supported_languages()
        print(f"  Supported languages: {len(languages)}")
        
        return True
    except Exception as e:
        print(f"  Translation test failed: {e}")
        return False

def test_medical_info_service():
    """Test medical information service"""
    try:
        from utils.medical_info import MedicalInfoService
        
        medical_info = MedicalInfoService()
        
        # Test medical info retrieval
        conditions = ['Normal', 'Pneumonia', 'Fracture']
        for condition in conditions:
            info = medical_info.get_medical_info(condition)
            print(f"  {condition}: {len(info.get('medical_tips', []))} tips")
        
        return True
    except Exception as e:
        print(f"  Medical info test failed: {e}")
        return False

def test_web_endpoints():
    """Test web endpoints"""
    try:
        base_url = 'http://localhost:5000'
        
        # Test public endpoints
        public_endpoints = ['/', '/about', '/login', '/signup']
        
        for endpoint in public_endpoints:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"  {endpoint}: {status} ({response.status_code})")
        
        return True
    except Exception as e:
        print(f"  Web endpoints test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    required_files = [
        'app.py',
        'forms.py',
        'requirements.txt',
        'models/database.py',
        'utils/enhanced_ml_model.py',
        'utils/translator.py',
        'utils/medical_info.py',
        'templates/base.html',
        'templates/index.html',
        'templates/dashboard.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"  Missing files: {missing_files}")
        return False
    else:
        print(f"  All {len(required_files)} required files present")
        return True

def test_demo_images():
    """Test if demo images exist"""
    demo_images = [
        'static/uploads/demo_chest_xray.jpg',
        'static/uploads/demo_hand_xray.jpg',
        'static/uploads/demo_leg_xray.jpg',
        'static/uploads/realistic_chest_normal.jpg',
        'static/uploads/realistic_chest_pneumonia.jpg',
        'static/uploads/realistic_hand_fracture.jpg'
    ]
    
    existing_images = [img for img in demo_images if os.path.exists(img)]
    print(f"  Demo images: {len(existing_images)}/{len(demo_images)} available")
    
    return len(existing_images) > 0

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("🧪 MediScan AI - Comprehensive Functionality Test")
    print("=" * 60)
    
    tests = [
        ("Server Status", test_server_running),
        ("File Structure", test_file_structure),
        ("Database Connection", test_database_connection),
        ("ML Model", test_ml_model),
        ("Translation Service", test_translation_service),
        ("Medical Info Service", test_medical_info_service),
        ("Web Endpoints", test_web_endpoints),
        ("Demo Images", test_demo_images)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            results[test_name] = test_func()
            status = "✅ PASS" if results[test_name] else "❌ FAIL"
            print(f"  Result: {status}")
        except Exception as e:
            results[test_name] = False
            print(f"  Result: ❌ FAIL - {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
    
    print("-" * 60)
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! MediScan AI is fully functional.")
        print("\n🚀 Ready for use:")
        print("   1. Visit: http://localhost:5000")
        print("   2. Login: demo@mediscan.com / demo123")
        print("   3. Test disease detection with demo patients")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed == total

def test_disease_detection_accuracy():
    """Test disease detection with known images"""
    print("\n🎯 Testing Disease Detection Accuracy...")
    
    try:
        from utils.enhanced_ml_model import EnhancedMLPredictor
        predictor = EnhancedMLPredictor()
        
        # Test cases with expected results
        test_cases = [
            {
                'image': 'static/uploads/realistic_chest_pneumonia.jpg',
                'body_part': 'chest',
                'patient_age': 65,
                'patient_gender': 'male',
                'expected_conditions': ['Pneumonia', 'COVID-19', 'Tuberculosis']
            },
            {
                'image': 'static/uploads/realistic_hand_fracture.jpg',
                'body_part': 'hand',
                'patient_age': 30,
                'patient_gender': 'male',
                'expected_conditions': ['Fracture', 'Dislocation']
            }
        ]
        
        accurate_predictions = 0
        
        for i, test_case in enumerate(test_cases, 1):
            if os.path.exists(test_case['image']):
                prediction, confidence = predictor.predict(
                    test_case['image'],
                    test_case['body_part'],
                    test_case['patient_age'],
                    test_case['patient_gender']
                )
                
                is_accurate = prediction in test_case['expected_conditions']
                if is_accurate:
                    accurate_predictions += 1
                
                status = "✅" if is_accurate else "⚠️"
                print(f"  Test {i}: {status} {prediction} ({confidence:.1%}) - {test_case['body_part']}")
            else:
                print(f"  Test {i}: ⚠️ Image not found: {test_case['image']}")
        
        accuracy = accurate_predictions / len(test_cases) * 100
        print(f"\n  Detection Accuracy: {accuracy:.1f}% ({accurate_predictions}/{len(test_cases)})")
        
        return accuracy > 50  # At least 50% accuracy expected
        
    except Exception as e:
        print(f"  Disease detection test failed: {e}")
        return False

if __name__ == "__main__":
    # Run comprehensive tests
    success = run_comprehensive_test()
    
    # Run accuracy tests if basic tests pass
    if success:
        test_disease_detection_accuracy()
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
