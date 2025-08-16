#!/usr/bin/env python3
"""
Create X-ray images with specific conditions that the AI can accurately detect
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import random

def create_chest_pneumonia_xray():
    """Create chest X-ray showing pneumonia (white consolidation patches)"""
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color=(15, 15, 20))
    draw = ImageDraw.Draw(img)
    
    # Basic chest structure
    # Lung fields
    left_lung = [(80, 120), (200, 100), (220, 300), (100, 320)]
    right_lung = [(300, 100), (420, 120), (400, 320), (280, 300)]
    draw.polygon(left_lung, fill=(35, 35, 40))
    draw.polygon(right_lung, fill=(35, 35, 40))
    
    # Add prominent white patches (consolidation) - key feature for pneumonia detection
    # Multiple white patches in both lungs
    consolidation_patches = [
        [120, 180, 180, 240],  # Left lung consolidation
        [320, 160, 380, 220],  # Right lung consolidation
        [140, 220, 170, 250],  # Additional left patch
        [340, 200, 370, 230]   # Additional right patch
    ]
    
    for patch in consolidation_patches:
        draw.ellipse(patch, fill=(120, 120, 130))  # Bright white patches
    
    # Add ribs and spine
    for i in range(8):
        y = 80 + i * 35
        draw.arc([60, y, 240, y + 40], 0, 180, fill=(60, 60, 70), width=2)
        draw.arc([260, y, 440, y + 40], 0, 180, fill=(60, 60, 70), width=2)
    draw.rectangle([245, 60, 255, 400], fill=(80, 80, 90))
    
    # Heart shadow
    heart_points = [(200, 200), (250, 180), (300, 200), (280, 280), (220, 280)]
    draw.polygon(heart_points, fill=(25, 25, 30))
    
    return img

def create_chest_covid_xray():
    """Create chest X-ray showing COVID-19 (ground-glass opacities)"""
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color=(15, 15, 20))
    draw = ImageDraw.Draw(img)
    
    # Basic chest structure
    left_lung = [(80, 120), (200, 100), (220, 300), (100, 320)]
    right_lung = [(300, 100), (420, 120), (400, 320), (280, 300)]
    draw.polygon(left_lung, fill=(38, 38, 43))
    draw.polygon(right_lung, fill=(38, 38, 43))
    
    # Add ground-glass opacities (many small patches) - key feature for COVID detection
    for i in range(25):  # More patches than pneumonia
        x = random.randint(100, 200)
        y = random.randint(150, 280)
        size = random.randint(15, 25)
        draw.ellipse([x, y, x+size, y+size], fill=(65, 65, 75))
    
    for i in range(20):
        x = random.randint(300, 400)
        y = random.randint(140, 290)
        size = random.randint(12, 22)
        draw.ellipse([x, y, x+size, y+size], fill=(62, 62, 72))
    
    # Add ribs and spine
    for i in range(8):
        y = 80 + i * 35
        draw.arc([60, y, 240, y + 40], 0, 180, fill=(60, 60, 70), width=2)
        draw.arc([260, y, 440, y + 40], 0, 180, fill=(60, 60, 70), width=2)
    draw.rectangle([245, 60, 255, 400], fill=(80, 80, 90))
    
    return img

def create_hand_fracture_xray():
    """Create hand X-ray showing clear fracture"""
    width, height = 400, 500
    img = Image.new('RGB', (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # Draw hand bones with clear fracture in middle finger
    finger_positions = [80, 120, 160, 200, 240]
    for i, x in enumerate(finger_positions):
        finger_length = 200 if i != 0 else 150
        
        if i == 2:  # Middle finger with fracture
            # Draw broken bone with clear fracture line
            draw.rectangle([x, 100, x + 15, 180], fill=(120, 120, 130))
            draw.rectangle([x, 190, x + 15, 100 + finger_length], fill=(120, 120, 130))
            # Prominent fracture line - key feature for fracture detection
            draw.line([(x-5, 185), (x + 20, 185)], fill=(40, 40, 50), width=8)
            # Displaced fragments
            draw.polygon([(x, 180), (x + 15, 180), (x + 20, 190), (x - 5, 190)], fill=(70, 70, 80))
        else:
            # Normal finger bones
            draw.rectangle([x, 100, x + 15, 100 + finger_length], fill=(120, 120, 130))
    
    # Palm and wrist bones
    for i in range(5):
        x = 70 + i * 60
        draw.rectangle([x, 300, x + 20, 380], fill=(110, 110, 120))
    
    return img

def create_hand_arthritis_xray():
    """Create hand X-ray showing arthritis"""
    width, height = 400, 500
    img = Image.new('RGB', (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # Draw hand bones with arthritis features
    finger_positions = [80, 120, 160, 200, 240]
    for i, x in enumerate(finger_positions):
        finger_length = 200 if i != 0 else 150
        
        # Thinner bones (bone loss)
        draw.rectangle([x, 100, x + 12, 100 + finger_length], fill=(100, 100, 110))
        
        # Joint space narrowing - key feature for arthritis detection
        draw.rectangle([x - 2, 148, x + 14, 152], fill=(40, 40, 50))  # Narrowed joint
        draw.rectangle([x - 2, 198, x + 14, 202], fill=(40, 40, 50))  # Narrowed joint
        
        # Bone spurs (osteophytes)
        draw.ellipse([x + 10, 145, x + 18, 155], fill=(130, 130, 140))
        draw.ellipse([x + 10, 195, x + 18, 205], fill=(130, 130, 140))
    
    # Palm bones with arthritis changes
    for i in range(5):
        x = 70 + i * 60
        draw.rectangle([x, 300, x + 18, 380], fill=(95, 95, 105))  # Thinner bones
    
    return img

def create_normal_chest_xray():
    """Create normal chest X-ray"""
    width, height = 512, 512
    img = Image.new('RGB', (width, height), color=(15, 15, 20))
    draw = ImageDraw.Draw(img)
    
    # Clear, normal lung fields
    left_lung = [(80, 120), (200, 100), (220, 300), (100, 320)]
    right_lung = [(300, 100), (420, 120), (400, 320), (280, 300)]
    draw.polygon(left_lung, fill=(40, 40, 45))  # Clear lungs
    draw.polygon(right_lung, fill=(40, 40, 45))
    
    # Normal ribs and spine
    for i in range(8):
        y = 80 + i * 35
        draw.arc([60, y, 240, y + 40], 0, 180, fill=(60, 60, 70), width=2)
        draw.arc([260, y, 440, y + 40], 0, 180, fill=(60, 60, 70), width=2)
    draw.rectangle([245, 60, 255, 400], fill=(80, 80, 90))
    
    # Normal heart shadow
    heart_points = [(200, 200), (250, 180), (300, 200), (280, 280), (220, 280)]
    draw.polygon(heart_points, fill=(25, 25, 30))
    
    return img

def create_normal_hand_xray():
    """Create normal hand X-ray"""
    width, height = 400, 500
    img = Image.new('RGB', (width, height), color=(20, 20, 25))
    draw = ImageDraw.Draw(img)
    
    # Normal finger bones
    finger_positions = [80, 120, 160, 200, 240]
    for i, x in enumerate(finger_positions):
        finger_length = 200 if i != 0 else 150
        # Normal, intact bones
        draw.rectangle([x, 100, x + 15, 100 + finger_length], fill=(120, 120, 130))
        # Normal joints
        draw.ellipse([x - 2, 150, x + 17, 160], fill=(100, 100, 110))
        draw.ellipse([x - 2, 200, x + 17, 210], fill=(100, 100, 110))
    
    # Normal palm and wrist bones
    for i in range(5):
        x = 70 + i * 60
        draw.rectangle([x, 300, x + 20, 380], fill=(110, 110, 120))
    
    return img

def main():
    """Create accurate test images for disease detection"""
    print("Creating accurate X-ray test images...")
    
    os.makedirs('static/uploads', exist_ok=True)
    
    # Create images with specific conditions
    test_images = [
        (create_chest_pneumonia_xray(), "test_chest_pneumonia.jpg"),
        (create_chest_covid_xray(), "test_chest_covid.jpg"),
        (create_normal_chest_xray(), "test_chest_normal.jpg"),
        (create_hand_fracture_xray(), "test_hand_fracture.jpg"),
        (create_hand_arthritis_xray(), "test_hand_arthritis.jpg"),
        (create_normal_hand_xray(), "test_hand_normal.jpg")
    ]
    
    for img, filename in test_images:
        # Add realistic noise and blur
        pixels = np.array(img)
        noise = np.random.normal(0, 8, pixels.shape).astype(np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Save image
        img.save(f'static/uploads/{filename}', 'JPEG', quality=90)
        print(f"Created: {filename}")
    
    print("\n✅ Accurate test images created!")
    print("These images contain specific features that the AI will detect:")
    print("• test_chest_pneumonia.jpg - Contains white consolidation patches")
    print("• test_chest_covid.jpg - Contains ground-glass opacities")
    print("• test_chest_normal.jpg - Clear, normal lung fields")
    print("• test_hand_fracture.jpg - Clear fracture line in middle finger")
    print("• test_hand_arthritis.jpg - Joint space narrowing and bone spurs")
    print("• test_hand_normal.jpg - Normal, intact bone structure")

if __name__ == "__main__":
    main()
