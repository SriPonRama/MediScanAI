#!/usr/bin/env python3
"""
Simple test to run the Flask app
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting Flask app test...")

try:
    from app import app
    print("App imported successfully!")
    
    print("Starting Flask development server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
    
except Exception as e:
    print(f"Error starting app: {e}")
    import traceback
    traceback.print_exc()
