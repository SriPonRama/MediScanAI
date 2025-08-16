#!/usr/bin/env python3
"""
Create demo X-ray images for MediScan AI
Generates placeholder images for demonstration
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_xray_placeholder(width=400, height=400, text="X-RAY", filename="demo_xray.jpg"):
    """Create a placeholder X-ray image"""
    # Create a dark background (typical of X-rays)
    img = Image.new('RGB', (width, height), color=(20, 20, 30))
    draw = ImageDraw.Draw(img)
    
    # Add some noise to make it look more realistic
    pixels = np.array(img)
    noise = np.random.normal(0, 10, pixels.shape).astype(np.uint8)
    pixels = np.clip(pixels + noise, 0, 255)
    img = Image.fromarray(pixels)
    draw = ImageDraw.Draw(img)
    
    # Add some bone-like structures (simple shapes)
    # Chest X-ray simulation
    if "chest" in filename:
        # Rib cage simulation
        for i in range(6):
            y = 100 + i * 30
            draw.ellipse([50, y, 350, y + 20], fill=(180, 180, 190), outline=(200, 200, 210))
        
        # Spine simulation
        draw.rectangle([190, 50, 210, 350], fill=(220, 220, 230))
        
        # Heart shadow
        draw.ellipse([120, 150, 200, 250], fill=(80, 80, 90))
    
    elif "hand" in filename:
        # Finger bones
        for i in range(5):
            x = 60 + i * 60
            draw.rectangle([x, 100, x + 15, 300], fill=(200, 200, 210))
            draw.rectangle([x, 80, x + 15, 120], fill=(200, 200, 210))
            draw.rectangle([x, 60, x + 15, 100], fill=(200, 200, 210))
        
        # Palm bones
        draw.ellipse([80, 250, 280, 350], fill=(180, 180, 190))
    
    elif "leg" in filename:
        # Femur
        draw.rectangle([180, 50, 220, 200], fill=(220, 220, 230))
        # Tibia and fibula
        draw.rectangle([170, 200, 200, 350], fill=(210, 210, 220))
        draw.rectangle([210, 200, 230, 350], fill=(210, 210, 220))
    
    # Add text label
    try:
        # Try to use a default font
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Get text size and center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = height - 50
    
    draw.text((x, y), text, fill=(150, 150, 160), font=font)
    
    return img

def create_hero_medical_svg():
    """Create a simple SVG for the hero section"""
    svg_content = '''
    <svg width="500" height="400" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#e3f2fd;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#f3e5f5;stop-opacity:1" />
            </linearGradient>
        </defs>
        
        <!-- Background -->
        <rect width="500" height="400" fill="url(#bg)"/>
        
        <!-- Medical cross -->
        <rect x="220" y="150" width="60" height="20" fill="#0d6efd" rx="10"/>
        <rect x="240" y="130" width="20" height="60" fill="#0d6efd" rx="10"/>
        
        <!-- Stethoscope -->
        <circle cx="150" cy="200" r="15" fill="none" stroke="#198754" stroke-width="3"/>
        <path d="M 150 185 Q 120 160 100 180 Q 80 200 100 220 Q 120 240 150 215" 
              fill="none" stroke="#198754" stroke-width="3"/>
        
        <!-- Heart -->
        <path d="M 350 180 C 340 170, 320 170, 320 190 C 320 170, 300 170, 290 180 
                 C 290 200, 320 220, 320 220 C 320 220, 350 200, 350 180 Z" 
              fill="#dc3545"/>
        
        <!-- Brain -->
        <ellipse cx="250" cy="100" rx="40" ry="30" fill="#6f42c1"/>
        <path d="M 220 90 Q 230 80 240 90 Q 250 80 260 90 Q 270 80 280 90" 
              fill="none" stroke="#fff" stroke-width="2"/>
        
        <!-- DNA Helix -->
        <path d="M 400 120 Q 420 140 400 160 Q 380 180 400 200 Q 420 220 400 240" 
              fill="none" stroke="#fd7e14" stroke-width="3"/>
        <path d="M 380 120 Q 400 140 380 160 Q 360 180 380 200 Q 400 220 380 240" 
              fill="none" stroke="#fd7e14" stroke-width="3"/>
        
        <!-- AI Circuit -->
        <circle cx="100" cy="100" r="8" fill="#20c997"/>
        <circle cx="120" cy="120" r="6" fill="#20c997"/>
        <circle cx="80" cy="120" r="6" fill="#20c997"/>
        <line x1="100" y1="108" x2="120" y2="114" stroke="#20c997" stroke-width="2"/>
        <line x1="100" y1="108" x2="80" y2="114" stroke="#20c997" stroke-width="2"/>
        
        <!-- Text -->
        <text x="250" y="350" text-anchor="middle" font-family="Arial, sans-serif" 
              font-size="24" font-weight="bold" fill="#0d6efd">MediScan AI</text>
        <text x="250" y="375" text-anchor="middle" font-family="Arial, sans-serif" 
              font-size="14" fill="#6c757d">AI-Powered Medical Diagnosis</text>
    </svg>
    '''
    return svg_content

def main():
    """Create all demo images"""
    # Ensure directories exist
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/uploads', exist_ok=True)
    
    print("Creating demo X-ray images...")
    
    # Create demo X-ray images
    images_to_create = [
        ("demo_chest_xray.jpg", "CHEST X-RAY"),
        ("demo_hand_xray.jpg", "HAND X-RAY"),
        ("demo_leg_xray.jpg", "LEG X-RAY"),
        ("demo_skull_xray.jpg", "SKULL X-RAY"),
        ("demo_spine_xray.jpg", "SPINE X-RAY"),
        ("demo_pelvis_xray.jpg", "PELVIS X-RAY")
    ]
    
    for filename, text in images_to_create:
        print(f"Creating {filename}...")
        img = create_xray_placeholder(text=text, filename=filename)
        img.save(f'static/uploads/{filename}', 'JPEG', quality=85)
    
    # Create hero medical illustration
    print("Creating hero medical illustration...")
    svg_content = create_hero_medical_svg()
    with open('static/images/hero-medical.svg', 'w') as f:
        f.write(svg_content)
    
    print("\nDemo images created successfully!")
    print("Files created:")
    print("- static/uploads/demo_*_xray.jpg (6 files)")
    print("- static/images/hero-medical.svg")

if __name__ == "__main__":
    main()
