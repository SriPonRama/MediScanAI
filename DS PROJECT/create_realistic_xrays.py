#!/usr/bin/env python3
"""
Create more realistic X-ray images for testing disease detection
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

def create_realistic_chest_xray(condition="Normal", filename="chest_xray.jpg"):
    """Create a realistic chest X-ray with specific condition"""
    width, height = 512, 512
    
    # Create base X-ray background
    img = Image.new('RGB', (width, height), color=(15, 15, 20))
    draw = ImageDraw.Draw(img)
    
    # Add lung fields
    left_lung = [(80, 120), (200, 100), (220, 300), (100, 320)]
    right_lung = [(300, 100), (420, 120), (400, 320), (280, 300)]
    
    # Draw lung fields with different intensities based on condition
    if condition == "Normal":
        lung_color = (40, 40, 45)
        draw.polygon(left_lung, fill=lung_color)
        draw.polygon(right_lung, fill=lung_color)
    elif condition == "Pneumonia":
        # Pneumonia shows as white patches (consolidation)
        lung_color = (35, 35, 40)
        draw.polygon(left_lung, fill=lung_color)
        draw.polygon(right_lung, fill=lung_color)
        # Add consolidation patches
        draw.ellipse([120, 180, 180, 240], fill=(80, 80, 90))
        draw.ellipse([320, 160, 380, 220], fill=(75, 75, 85))
    elif condition == "COVID-19":
        # COVID-19 shows ground-glass opacities
        lung_color = (38, 38, 43)
        draw.polygon(left_lung, fill=lung_color)
        draw.polygon(right_lung, fill=lung_color)
        # Add ground-glass patterns
        for i in range(15):
            x = random.randint(100, 200)
            y = random.randint(150, 280)
            draw.ellipse([x, y, x+20, y+20], fill=(55, 55, 65))
        for i in range(12):
            x = random.randint(300, 400)
            y = random.randint(140, 290)
            draw.ellipse([x, y, x+18, y+18], fill=(52, 52, 62))
    
    # Add rib cage
    for i in range(8):
        y = 80 + i * 35
        # Left ribs
        draw.arc([60, y, 240, y + 40], 0, 180, fill=(60, 60, 70), width=2)
        # Right ribs
        draw.arc([260, y, 440, y + 40], 0, 180, fill=(60, 60, 70), width=2)
    
    # Add spine
    draw.rectangle([245, 60, 255, 400], fill=(80, 80, 90))
    
    # Add heart shadow
    heart_points = [(200, 200), (250, 180), (300, 200), (280, 280), (220, 280)]
    draw.polygon(heart_points, fill=(25, 25, 30))
    
    # Add some noise and texture
    pixels = np.array(img)
    noise = np.random.normal(0, 8, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    # Apply slight blur to simulate X-ray characteristics
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    return img

def create_realistic_hand_xray(condition="Normal", filename="hand_xray.jpg"):
    """Create a realistic hand X-ray"""
    width, height = 400, 500
    img = Image.new('RGB', (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # Draw hand bones
    # Fingers
    finger_positions = [80, 120, 160, 200, 240]
    for i, x in enumerate(finger_positions):
        finger_length = 200 if i != 0 else 150  # Thumb is shorter
        
        if condition == "Fracture" and i == 2:  # Fracture in middle finger
            # Draw broken bone
            draw.rectangle([x, 100, x + 15, 180], fill=(120, 120, 130))
            draw.rectangle([x, 190, x + 15, 100 + finger_length], fill=(120, 120, 130))
            # Add fracture line
            draw.line([(x, 185), (x + 15, 185)], fill=(80, 80, 90), width=3)
        else:
            # Normal finger bones
            draw.rectangle([x, 100, x + 15, 100 + finger_length], fill=(120, 120, 130))
            # Finger joints
            draw.ellipse([x - 2, 150, x + 17, 160], fill=(100, 100, 110))
            draw.ellipse([x - 2, 200, x + 17, 210], fill=(100, 100, 110))
    
    # Palm bones
    palm_bones = [
        [70, 300, 90, 380],
        [110, 300, 130, 380],
        [150, 300, 170, 380],
        [190, 300, 210, 380],
        [230, 300, 250, 380]
    ]
    
    for bone in palm_bones:
        draw.rectangle(bone, fill=(110, 110, 120))
    
    # Wrist bones
    wrist_bones = [
        [80, 380, 100, 400],
        [110, 380, 130, 400],
        [140, 380, 160, 400],
        [170, 380, 190, 400],
        [200, 380, 220, 400],
        [230, 380, 250, 400]
    ]
    
    for bone in wrist_bones:
        draw.ellipse(bone, fill=(115, 115, 125))
    
    # Add arthritis effects if needed
    if condition == "Arthritis":
        # Add joint space narrowing and bone spurs
        for i, x in enumerate(finger_positions):
            # Joint space narrowing
            draw.rectangle([x - 1, 148, x + 16, 152], fill=(60, 60, 70))
            draw.rectangle([x - 1, 198, x + 16, 202], fill=(60, 60, 70))
            # Bone spurs
            draw.ellipse([x + 12, 145, x + 20, 155], fill=(130, 130, 140))
    
    # Add noise
    pixels = np.array(img)
    noise = np.random.normal(0, 6, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    return img

def create_realistic_leg_xray(condition="Normal", filename="leg_xray.jpg"):
    """Create a realistic leg X-ray"""
    width, height = 300, 600
    img = Image.new('RGB', (width, height), color=(18, 18, 23))
    draw = ImageDraw.Draw(img)
    
    # Femur (thigh bone)
    if condition == "Fracture":
        # Draw fractured femur
        draw.rectangle([140, 50, 160, 250], fill=(130, 130, 140))
        draw.rectangle([140, 260, 160, 350], fill=(130, 130, 140))
        # Fracture line
        draw.line([(135, 255), (165, 255)], fill=(70, 70, 80), width=4)
        # Displaced fragments
        draw.polygon([(140, 250), (160, 250), (165, 260), (135, 260)], fill=(90, 90, 100))
    else:
        # Normal femur
        draw.rectangle([140, 50, 160, 350], fill=(130, 130, 140))
    
    # Tibia (shin bone)
    draw.rectangle([135, 350, 155, 550], fill=(125, 125, 135))
    
    # Fibula (smaller bone)
    draw.rectangle([170, 360, 180, 540], fill=(120, 120, 130))
    
    # Knee joint
    draw.ellipse([130, 340, 170, 360], fill=(100, 100, 110))
    
    # Add soft tissue shadows
    draw.ellipse([80, 100, 220, 500], fill=(30, 30, 35), outline=None)
    
    # Add arthritis effects if needed
    if condition == "Arthritis":
        # Joint space narrowing
        draw.rectangle([132, 348, 168, 352], fill=(50, 50, 60))
        # Bone spurs
        draw.ellipse([125, 345, 135, 355], fill=(140, 140, 150))
        draw.ellipse([165, 345, 175, 355], fill=(140, 140, 150))
    
    # Add noise
    pixels = np.array(img)
    noise = np.random.normal(0, 7, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    return img

def main():
    """Create realistic X-ray images for testing"""
    print("Creating realistic X-ray images for disease detection testing...")
    
    # Ensure upload directory exists
    os.makedirs('static/uploads', exist_ok=True)
    
    # Create chest X-rays with different conditions
    chest_conditions = [
        ("Normal", "realistic_chest_normal.jpg"),
        ("Pneumonia", "realistic_chest_pneumonia.jpg"),
        ("COVID-19", "realistic_chest_covid.jpg")
    ]
    
    for condition, filename in chest_conditions:
        print(f"Creating chest X-ray: {condition}")
        img = create_realistic_chest_xray(condition, filename)
        img.save(f'static/uploads/{filename}', 'JPEG', quality=90)
    
    # Create hand X-rays
    hand_conditions = [
        ("Normal", "realistic_hand_normal.jpg"),
        ("Fracture", "realistic_hand_fracture.jpg"),
        ("Arthritis", "realistic_hand_arthritis.jpg")
    ]
    
    for condition, filename in hand_conditions:
        print(f"Creating hand X-ray: {condition}")
        img = create_realistic_hand_xray(condition, filename)
        img.save(f'static/uploads/{filename}', 'JPEG', quality=90)
    
    # Create leg X-rays
    leg_conditions = [
        ("Normal", "realistic_leg_normal.jpg"),
        ("Fracture", "realistic_leg_fracture.jpg"),
        ("Arthritis", "realistic_leg_arthritis.jpg")
    ]
    
    for condition, filename in leg_conditions:
        print(f"Creating leg X-ray: {condition}")
        img = create_realistic_leg_xray(condition, filename)
        img.save(f'static/uploads/{filename}', 'JPEG', quality=90)
    
    print("\nRealistic X-ray images created successfully!")
    print("Files created in static/uploads/:")
    print("- realistic_chest_*.jpg (3 files)")
    print("- realistic_hand_*.jpg (3 files)")  
    print("- realistic_leg_*.jpg (3 files)")
    print("\nThese images can be used to test the enhanced disease detection system.")

if __name__ == "__main__":
    main()
