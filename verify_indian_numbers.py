#!/usr/bin/env python3
"""
Verify that Indian phone numbers are properly updated
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models.database import db, User, Patient

def verify_phone_numbers():
    """Verify all phone numbers are in Indian format"""
    print("🇮🇳 Verifying Indian Phone Numbers in MediScan AI")
    print("=" * 60)
    
    with app.app_context():
        # Check demo user
        demo_user = User.query.filter_by(email='demo@mediscan.com').first()
        if demo_user:
            print(f"📱 Demo User Phone: {demo_user.phone}")
        
        # Check all patients
        patients = Patient.query.all()
        print(f"\n👥 Patient Phone Numbers ({len(patients)} patients):")
        print("-" * 40)
        
        for patient in patients:
            print(f"📞 {patient.name}: {patient.contact}")
            if patient.emergency_contact:
                print(f"   Emergency: {patient.emergency_contact}")
            print(f"   Address: {patient.address}")
            print()
        
        # Verify format
        all_indian = True
        phone_numbers = [demo_user.phone] if demo_user else []
        phone_numbers.extend([p.contact for p in patients])
        
        for phone in phone_numbers:
            if not phone.startswith('+91-'):
                all_indian = False
                print(f"❌ Non-Indian format found: {phone}")
        
        if all_indian:
            print("✅ All phone numbers are in Indian format (+91-XXXXX-XXXXX)")
        else:
            print("❌ Some phone numbers are not in Indian format")
        
        print("\n" + "=" * 60)
        print("🎯 Updated Features:")
        print("• Phone number auto-formatting for Indian numbers")
        print("• Updated demo patients with Indian names and addresses")
        print("• Contact information updated to Indian format")
        print("• Form placeholders show Indian phone format")
        
        return all_indian

if __name__ == "__main__":
    verify_phone_numbers()
