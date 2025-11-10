#!/usr/bin/env python3
"""
Fix phone number formats to ensure all are in Indian format
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.database import db, User, Patient

def format_indian_phone(phone):
    """Format phone number to Indian format"""
    if not phone:
        return phone
    
    # Remove all non-digits
    digits = ''.join(filter(str.isdigit, phone))
    
    # Handle different cases
    if digits.startswith('91') and len(digits) == 12:
        # Already has country code
        return f"+91-{digits[2:7]}-{digits[7:12]}"
    elif len(digits) == 10:
        # Indian mobile number without country code
        return f"+91-{digits[:5]}-{digits[5:]}"
    else:
        # Return as is if format is unclear
        return phone

def fix_all_phone_numbers():
    """Fix all phone numbers in the database"""
    print("🔧 Fixing Phone Number Formats")
    print("=" * 40)
    
    with app.app_context():
        # Fix demo user phone
        demo_user = User.query.filter_by(email='demo@mediscan.com').first()
        if demo_user:
            old_phone = demo_user.phone
            demo_user.phone = format_indian_phone(demo_user.phone)
            print(f"User: {old_phone} → {demo_user.phone}")
        
        # Fix all patient phones
        patients = Patient.query.all()
        for patient in patients:
            old_contact = patient.contact
            old_emergency = patient.emergency_contact
            
            patient.contact = format_indian_phone(patient.contact)
            if patient.emergency_contact:
                patient.emergency_contact = format_indian_phone(patient.emergency_contact)
            
            print(f"Patient {patient.name}:")
            print(f"  Contact: {old_contact} → {patient.contact}")
            if old_emergency:
                print(f"  Emergency: {old_emergency} → {patient.emergency_contact}")
        
        # Commit changes
        db.session.commit()
        print("\n✅ All phone numbers updated successfully!")
        
        # Verify the changes
        print("\n📱 Updated Phone Numbers:")
        print("-" * 30)
        if demo_user:
            print(f"Demo User: {demo_user.phone}")
        
        for patient in Patient.query.all():
            print(f"{patient.name}: {patient.contact}")
            if patient.emergency_contact:
                print(f"  Emergency: {patient.emergency_contact}")

if __name__ == "__main__":
    fix_all_phone_numbers()
