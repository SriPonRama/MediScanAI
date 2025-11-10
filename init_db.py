#!/usr/bin/env python3
"""
Database initialization script for MediScan AI
Creates tables and adds demo data
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.database import db, User, Patient, Prediction

def init_database():
    """Initialize database with tables and demo data"""
    with app.app_context():
        # Drop all tables and recreate (for development)
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Create demo user
        print("Creating demo user...")
        demo_user = User(
            name="Demo User",
            email="demo@mediscan.com",
            phone="+91-98765-43210"
        )
        demo_user.set_password("demo123")
        db.session.add(demo_user)
        db.session.commit()
        
        # Create demo patients
        print("Creating demo patients...")
        patients_data = [
            {
                "name": "Rajesh Kumar",
                "age": 45,
                "gender": "male",
                "contact": "+91-98765-12345",
                "address": "123 MG Road, Bangalore, Karnataka 560001",
                "medical_history": "Hypertension, previous chest infection in 2020",
                "blood_group": "O+",
                "allergies": "Penicillin"
            },
            {
                "name": "Priya Sharma",
                "age": 32,
                "gender": "female",
                "contact": "+91-87654-32109",
                "address": "456 Connaught Place, New Delhi, Delhi 110001",
                "medical_history": "No significant medical history",
                "blood_group": "A+",
                "allergies": "None known"
            },
            {
                "name": "Arjun Patel",
                "age": 28,
                "gender": "male",
                "contact": "+91-76543-21098",
                "address": "789 Marine Drive, Mumbai, Maharashtra 400001",
                "medical_history": "Previous fracture in left arm (2019)",
                "blood_group": "B-",
                "allergies": "Shellfish"
            }
        ]
        
        demo_patients = []
        for patient_data in patients_data:
            patient = Patient(
                user_id=demo_user.id,
                **patient_data
            )
            db.session.add(patient)
            demo_patients.append(patient)
        
        db.session.commit()
        
        # Create demo predictions
        print("Creating demo predictions...")
        predictions_data = [
            {
                "patient": demo_patients[0],
                "image_path": "demo_chest_xray.jpg",
                "body_part": "chest",
                "prediction_result": "Pneumonia",
                "confidence_score": 0.87,
                "additional_info": '{"condition": "Pneumonia", "description": "Infection that inflames air sacs in lungs"}',
                "medical_tips": '["Get plenty of rest", "Take prescribed antibiotics", "Stay hydrated"]'
            },
            {
                "patient": demo_patients[1],
                "image_path": "demo_hand_xray.jpg",
                "body_part": "hand",
                "prediction_result": "Normal",
                "confidence_score": 0.94,
                "additional_info": '{"condition": "Normal", "description": "No abnormalities detected"}',
                "medical_tips": '["Maintain regular exercise", "Eat calcium-rich foods"]'
            },
            {
                "patient": demo_patients[2],
                "image_path": "demo_leg_xray.jpg",
                "body_part": "leg",
                "prediction_result": "Fracture",
                "confidence_score": 0.91,
                "additional_info": '{"condition": "Fracture", "description": "Break or crack in bone"}',
                "medical_tips": '["Keep area immobilized", "Apply ice to reduce swelling", "Follow up with orthopedic specialist"]'
            }
        ]
        
        for pred_data in predictions_data:
            prediction = Prediction(
                patient_id=pred_data["patient"].id,
                image_path=pred_data["image_path"],
                body_part=pred_data["body_part"],
                prediction_result=pred_data["prediction_result"],
                confidence_score=pred_data["confidence_score"],
                additional_info=pred_data["additional_info"],
                medical_tips=pred_data["medical_tips"],
                created_at=datetime.utcnow()
            )
            db.session.add(prediction)
        
        db.session.commit()
        
        print("\n" + "="*50)
        print("Database initialized successfully!")
        print("="*50)
        print(f"Demo user created:")
        print(f"  Email: demo@mediscan.com")
        print(f"  Password: demo123")
        print(f"\nDemo patients created: {len(demo_patients)}")
        print(f"Demo predictions created: {len(predictions_data)}")
        print("="*50)

if __name__ == "__main__":
    init_database()
