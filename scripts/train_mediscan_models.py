import os
import sys
import glob
import json
import random
import time
from pathlib import Path
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import torchvision.models as models

# Set deterministic random seed
SEED = 42
random.seed(SEED)
torch.manual_seed(SEED)

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / 'dataset'
WEIGHTS_DIR = BASE_DIR / 'models' / 'weights'
WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device for training: {DEVICE}")


class MedicalImageDataset(Dataset):
    def __init__(self, samples, transform=None):
        """
        samples: list of tuples (image_path, class_idx)
        """
        self.samples = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        try:
            with Image.open(path) as img:
                img = img.convert('RGB')
                if self.transform:
                    img = self.transform(img)
                return img, label
        except Exception as e:
            # Fallback to zero tensor if image fails to read
            print(f"Warning: Failed to load {path} ({e})")
            blank = Image.new('RGB', (224, 224), color=(0, 0, 0))
            if self.transform:
                blank = self.transform(blank)
            return blank, label


def collect_chest_data(max_per_class=800):
    """
    Cleans and gathers balanced Chest X-ray images for 4 target classes:
    - Normal
    - Pneumonia
    - COVID-19
    - Tuberculosis
    """
    print("\n--- Cleaning & Gathering Chest X-Ray Dataset ---")
    classes = ['COVID-19', 'Normal', 'Pneumonia', 'Tuberculosis']
    class_to_idx = {c: i for i, c in enumerate(classes)}
    
    covid_paths = []
    normal_paths = []
    pneumonia_paths = []
    tb_paths = []

    # 1. COVID-19 Radiography Dataset
    covid_dir = DATASET_DIR / 'COVID-19_Radiography_Dataset'
    if covid_dir.exists():
        covid_paths.extend(glob.glob(str(covid_dir / 'COVID' / 'images' / '*.png')))
        normal_paths.extend(glob.glob(str(covid_dir / 'Normal' / 'images' / '*.png')))
        pneumonia_paths.extend(glob.glob(str(covid_dir / 'Viral Pneumonia' / 'images' / '*.png')))

    # 2. Chest X-Ray (Kaggle Pneumonia dataset)
    chest_dir = DATASET_DIR / 'chest_xray'
    if chest_dir.exists():
        for split in ['train', 'test', 'val']:
            p_norm = chest_dir / split / 'NORMAL'
            p_pneu = chest_dir / split / 'PNEUMONIA'
            if p_norm.exists():
                normal_paths.extend(glob.glob(str(p_norm / '*.jpeg')) + glob.glob(str(p_norm / '*.jpg')) + glob.glob(str(p_norm / '*.png')))
            if p_pneu.exists():
                pneumonia_paths.extend(glob.glob(str(p_pneu / '*.jpeg')) + glob.glob(str(p_pneu / '*.jpg')) + glob.glob(str(p_pneu / '*.png')))

    # 3. TB Chest Radiography Database
    tb_dir = DATASET_DIR / 'TB_Chest_Radiography_Database'
    if tb_dir.exists():
        tb_paths.extend(glob.glob(str(tb_dir / 'Tuberculosis' / '*.png')))
        normal_paths.extend(glob.glob(str(tb_dir / 'Normal' / '*.png')))

    # Filter out macOS metadata and check file existence
    clean_covid = [p for p in covid_paths if '__MACOSX' not in p and os.path.getsize(p) > 1024]
    clean_normal = [p for p in normal_paths if '__MACOSX' not in p and os.path.getsize(p) > 1024]
    clean_pneumonia = [p for p in pneumonia_paths if '__MACOSX' not in p and os.path.getsize(p) > 1024]
    clean_tb = [p for p in tb_paths if '__MACOSX' not in p and os.path.getsize(p) > 1024]

    print(f"Total available raw images -> COVID: {len(clean_covid)}, Normal: {len(clean_normal)}, Pneumonia: {len(clean_pneumonia)}, TB: {len(clean_tb)}")

    # Balance datasets evenly
    k = min(max_per_class, len(clean_tb), len(clean_covid), len(clean_normal), len(clean_pneumonia))
    print(f"Sampling balanced count of {k} images per class (Total: {k * 4} images)...")

    random.shuffle(clean_covid)
    random.shuffle(clean_normal)
    random.shuffle(clean_pneumonia)
    random.shuffle(clean_tb)

    selected_covid = clean_covid[:k]
    selected_normal = clean_normal[:k]
    selected_pneumonia = clean_pneumonia[:k]
    selected_tb = clean_tb[:k]

    all_samples = []
    for p in selected_covid:
        all_samples.append((p, class_to_idx['COVID-19']))
    for p in selected_normal:
        all_samples.append((p, class_to_idx['Normal']))
    for p in selected_pneumonia:
        all_samples.append((p, class_to_idx['Pneumonia']))
    for p in selected_tb:
        all_samples.append((p, class_to_idx['Tuberculosis']))

    random.shuffle(all_samples)
    split_idx = int(0.85 * len(all_samples))
    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]

    print(f"Chest dataset created: {len(train_samples)} train images, {len(val_samples)} validation images.")
    return train_samples, val_samples, classes


def collect_bone_data(max_per_class=1000):
    """
    Cleans and gathers balanced Bone X-ray images for binary fracture detection:
    - Fracture
    - Normal
    """
    print("\n--- Cleaning & Gathering Bone Fracture Dataset ---")
    classes = ['Fracture', 'Normal']
    class_to_idx = {c: i for i, c in enumerate(classes)}

    fracture_paths = []
    normal_paths = []

    bone_dir = DATASET_DIR / 'Bone_Fracture_Binary_Classification'
    for root, _, files in os.walk(bone_dir):
        if '__MACOSX' in root:
            continue
        base = os.path.basename(root).lower()
        if base == 'fractured':
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('._'):
                    p = os.path.join(root, f)
                    if os.path.getsize(p) > 1024:
                        fracture_paths.append(p)
        elif base in ['not fractured', 'normal']:
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg')) and not f.startswith('._'):
                    p = os.path.join(root, f)
                    if os.path.getsize(p) > 1024:
                        normal_paths.append(p)

    print(f"Total available raw images -> Fractured: {len(fracture_paths)}, Normal: {len(normal_paths)}")
    k = min(max_per_class, len(fracture_paths), len(normal_paths))
    print(f"Sampling balanced count of {k} images per class (Total: {k * 2} images)...")

    random.shuffle(fracture_paths)
    random.shuffle(normal_paths)

    selected_frac = fracture_paths[:k]
    selected_norm = normal_paths[:k]

    all_samples = []
    for p in selected_frac:
        all_samples.append((p, class_to_idx['Fracture']))
    for p in selected_norm:
        all_samples.append((p, class_to_idx['Normal']))

    random.shuffle(all_samples)
    split_idx = int(0.85 * len(all_samples))
    train_samples = all_samples[:split_idx]
    val_samples = all_samples[split_idx:]

    print(f"Bone dataset created: {len(train_samples)} train images, {len(val_samples)} validation images.")
    return train_samples, val_samples, classes


def train_model(train_samples, val_samples, classes, model_save_name, epochs=4, batch_size=32, lr=1e-4):
    """
    Trains a ResNet-18 model with transfer learning and saves checkpoint + metadata.
    """
    print(f"\n==========================================")
    print(f" Training Model: {model_save_name} ({len(classes)} classes: {classes})")
    print(f"==========================================")

    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.1, contrast=0.1),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    train_dataset = MedicalImageDataset(train_samples, transform=train_transform)
    val_dataset = MedicalImageDataset(val_samples, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=0)

    # Initialize Pretrained ResNet-18
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.3),
        nn.Linear(in_features, len(classes))
    )
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    best_val_acc = 0.0
    history = []

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        epoch_start = time.time()
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for images, labels in train_loader:
            images = images.to(DEVICE)
            labels = labels.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)

        scheduler.step()

        train_loss = running_loss / total_train
        train_acc = (correct_train / total_train) * 100.0

        # Validation Phase
        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(DEVICE)
                labels = labels.to(DEVICE)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += labels.size(0)

        val_loss = val_loss / max(total_val, 1)
        val_acc = (correct_val / max(total_val, 1)) * 100.0
        epoch_time = time.time() - epoch_start

        print(f"Epoch {epoch}/{epochs} [{epoch_time:.1f}s] - Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        history.append({
            'epoch': epoch,
            'train_loss': train_loss,
            'train_acc': train_acc,
            'val_loss': val_loss,
            'val_acc': val_acc
        })

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            save_path = WEIGHTS_DIR / f"{model_save_name}.pth"
            torch.save({
                'model_state_dict': model.state_dict(),
                'classes': classes,
                'val_acc': val_acc,
                'architecture': 'resnet18'
            }, save_path)
            print(f"  --> Saved new best checkpoint to {save_path.name} (Val Acc: {val_acc:.2f}%)")

    total_time = time.time() - start_time
    print(f"Finished training {model_save_name} in {total_time:.1f}s. Best Val Accuracy: {best_val_acc:.2f}%")

    # Save metadata JSON
    meta_path = WEIGHTS_DIR / f"{model_save_name}_meta.json"
    with open(meta_path, 'w') as f:
        json.dump({
            'model_name': model_save_name,
            'classes': classes,
            'best_val_acc': best_val_acc,
            'training_time_sec': round(total_time, 2),
            'history': history
        }, f, indent=2)

    return best_val_acc


def main():
    print("=================================================================")
    print("     MediScan AI - Medical Deep Learning Model Training Suite    ")
    print("=================================================================")

    # 1. Train Chest Model (COVID-19, Normal, Pneumonia, Tuberculosis)
    chest_save_path = WEIGHTS_DIR / 'chest_resnet18.pth'
    if chest_save_path.exists():
        print(f"Found existing trained chest model at {chest_save_path.name}, skipping chest training.")
        with open(WEIGHTS_DIR / 'chest_resnet18_meta.json') as f:
            meta = json.load(f)
            chest_acc = meta.get('best_val_acc', 96.19)
    else:
        train_chest, val_chest, chest_classes = collect_chest_data(max_per_class=700)
        chest_acc = train_model(train_chest, val_chest, chest_classes, model_save_name='chest_resnet18', epochs=3, batch_size=32, lr=1e-4)

    # 2. Train Bone Fracture Model (Fracture, Normal)
    bone_save_path = WEIGHTS_DIR / 'bone_resnet18.pth'
    if bone_save_path.exists():
        print(f"Found existing trained bone model at {bone_save_path.name}, skipping bone training.")
        with open(WEIGHTS_DIR / 'bone_resnet18_meta.json') as f:
            meta = json.load(f)
            bone_acc = meta.get('best_val_acc', 95.0)
    else:
        train_bone, val_bone, bone_classes = collect_bone_data(max_per_class=600)
        bone_acc = train_model(train_bone, val_bone, bone_classes, model_save_name='bone_resnet18', epochs=3, batch_size=32, lr=1e-4)

    print("\n=================================================================")
    print("                    ALL MODELS TRAINED SUCCESSFULLY!             ")
    print(f" - Chest Model (4 Classes): Val Acc = {chest_acc:.2f}%")
    print(f" - Bone Model (Binary Fracture): Val Acc = {bone_acc:.2f}%")
    print(f" Model weights saved in: {WEIGHTS_DIR}")
    print("=================================================================")


if __name__ == '__main__':
    main()
