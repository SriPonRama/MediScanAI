"""
MediScan AI — Continuous Deep Learning Fine-Tuning Engine
========================================================
Fine-tunes ResNet-18 architectures for:
  1. Chest X-Ray: 4 Classes (COVID-19, Normal, Pneumonia, Tuberculosis)
  2. Bone X-Ray: 2 Classes (Fracture, Normal)

Maintains full backward and forward compatibility with utils/enhanced_ml_model.py:
  - Architecture: ResNet-18 with nn.Sequential(nn.Dropout(0.3), nn.Linear(512, num_classes))
  - State format: {'model_state_dict': ..., 'classes': ..., 'val_acc': ..., 'architecture': 'resnet18'}
  - Epoch checkpoints & metadata persistence
"""

import os
import sys
import time
import json
import random
import numpy as np
from PIL import Image

# Force immediate console flushing
sys.stdout.reconfigure(line_buffering=True)

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.models as tv_models
import torchvision.transforms as T

BASE = r"c:\Users\dhuvarakesan\OneDrive\Desktop\Sri Pon Rama\projects\MediScanAI(DS)"
DS_DIR = os.path.join(BASE, "dataset")
WT_DIR = os.path.join(BASE, "models", "weights")
os.makedirs(WT_DIR, exist_ok=True)

# Performance acceleration for fast CPU execution
torch.set_num_threads(min(8, os.cpu_count() or 4))
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMG_SIZE = 224
BATCH_SIZE = 32
LR = 1.0e-5

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

print("=" * 65)
print(f" MediScan AI — Model Fine-Tuning Pipeline | Device: {DEVICE} (Threads: {torch.get_num_threads()})")
print("=" * 65)

# Fast, memory-efficient augmentations (no CPU bottleneck)
TRAIN_TRANSFORM = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.RandomHorizontalFlip(0.5),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

VAL_TRANSFORM = T.Compose([
    T.Resize((IMG_SIZE, IMG_SIZE)),
    T.ToTensor(),
    T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}

def collect_images_from_dir(folder, label_idx):
    image_paths = []
    if not os.path.isdir(folder):
        return image_paths
    for root, _, files in os.walk(folder):
        if '__MACOSX' in root:
            continue
        for f in files:
            if os.path.splitext(f)[1].lower() in EXTENSIONS:
                image_paths.append((os.path.join(root, f), label_idx))
    return image_paths

class MemoryOptimizedDataset(Dataset):
    def __init__(self, items, transform):
        self.items = items
        self.transform = transform

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        path, label = self.items[idx]
        try:
            img = Image.open(path).convert('RGB')
        except Exception:
            img = Image.new('RGB', (IMG_SIZE, IMG_SIZE), 128)
        return self.transform(img), label

def build_model(num_classes, checkpoint_path=None):
    model = tv_models.resnet18(weights=tv_models.ResNet18_Weights.DEFAULT)
    # Match enhanced_ml_model.py exactly:
    model.fc = nn.Sequential(nn.Dropout(0.3), nn.Linear(512, num_classes))

    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            cp = torch.load(checkpoint_path, map_location=DEVICE)
            if isinstance(cp, dict) and 'model_state_dict' in cp:
                model.load_state_dict(cp['model_state_dict'], strict=True)
                print(f"  [SUCCESS] Resumed weights from {os.path.basename(checkpoint_path)} (Val Acc: {cp.get('val_acc', 'N/A')}%)")
            else:
                model.load_state_dict(cp, strict=True)
                print(f"  [SUCCESS] Loaded raw state dict from {os.path.basename(checkpoint_path)}")
        except Exception as ex:
            print(f"  [WARN] Checkpoint loading warning: {ex}. Using ImageNet transfer weights.")
    
    # Freeze lower feature blocks to accelerate CPU backward pass
    for param in model.conv1.parameters():
        param.requires_grad = False
    for param in model.bn1.parameters():
        param.requires_grad = False
    for param in model.layer1.parameters():
        param.requires_grad = False
    for param in model.layer2.parameters():
        param.requires_grad = False

    return model.to(DEVICE)

def evaluate(model, loader, criterion):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for imgs, labels in loader:
            imgs, labels = imgs.to(DEVICE), labels.to(DEVICE)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            total_loss += loss.item() * imgs.size(0)
            _, preds = outputs.max(1)
            correct += preds.eq(labels).sum().item()
            total += imgs.size(0)
    return total_loss / max(total, 1), (100.0 * correct / max(total, 1))

def train_network(model_name, num_classes, class_names, train_items, val_items, extra_epochs=3):
    print(f"\n{'━'*65}")
    print(f" [PHASE] Training: {model_name.upper()}")
    print(f" Classes ({num_classes}): {class_names}")
    print(f" Train Samples: {len(train_items)} | Val Samples: {len(val_items)}")
    print(f"{'━'*65}")

    weights_file = os.path.join(WT_DIR, f"{model_name}.pth")
    meta_file = os.path.join(WT_DIR, f"{model_name}_meta.json")

    # Load existing metadata/history
    history = []
    best_val_acc = 0.0
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                existing_meta = json.load(f)
            history = existing_meta.get('history', [])
            best_val_acc = existing_meta.get('best_val_acc', 0.0)
            print(f" Existing history found: {len(history)} previous epochs logged. Current Best: {best_val_acc:.2f}%")
        except Exception:
            pass

    model = build_model(num_classes, weights_file)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.05)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=extra_epochs, eta_min=1e-6)

    train_loader = DataLoader(MemoryOptimizedDataset(train_items, TRAIN_TRANSFORM), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(MemoryOptimizedDataset(val_items, VAL_TRANSFORM), batch_size=BATCH_SIZE, shuffle=False)

    # Initial baseline check
    val_loss, val_acc = evaluate(model, val_loader, criterion)
    print(f" Baseline Validation: Loss = {val_loss:.4f}, Accuracy = {val_acc:.2f}%")
    if val_acc > best_val_acc:
        best_val_acc = val_acc

    start_epoch = len(history) + 1
    t_start = time.time()

    print(f"\n {'Epoch':>6}  {'Train Loss':>11}  {'Train Acc':>10}  {'Val Loss':>9}  {'Val Acc':>9}  {'Status':>10}")
    print(f" {'-'*62}")

    for i in range(extra_epochs):
        ep = start_epoch + i
        model.train()
        r_loss, correct, total = 0.0, 0, 0

        for batch_idx, (imgs, lbls) in enumerate(train_loader):
            imgs, lbls = imgs.to(DEVICE), lbls.to(DEVICE)
            optimizer.zero_grad()
            out = model(imgs)
            loss = criterion(out, lbls)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            r_loss += loss.item() * imgs.size(0)
            _, pred = out.max(1)
            correct += pred.eq(lbls).sum().item()
            total += imgs.size(0)

            if (batch_idx + 1) % 15 == 0 or (batch_idx + 1) == len(train_loader):
                print(f"   [Epoch {ep}] Batch {batch_idx+1}/{len(train_loader)}: Loss={r_loss/total:.4f}, Acc={100*correct/total:.2f}%", flush=True)

        train_loss = r_loss / total
        train_acc = 100.0 * correct / total

        v_loss, v_acc = evaluate(model, val_loader, criterion)
        scheduler.step()

        status_str = "Completed"
        if v_acc >= best_val_acc or i == 0:
            best_val_acc = max(v_acc, best_val_acc)
            status_str = "SAVED (Best)"
            
            # Save in the exact format enhanced_ml_model.py expects:
            checkpoint = {
                'model_state_dict': model.state_dict(),
                'classes': class_names,
                'val_acc': best_val_acc,
                'architecture': 'resnet18',
                'epoch': ep,
                'updated_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            torch.save(checkpoint, weights_file)

        history.append({
            'epoch': ep,
            'train_loss': round(train_loss, 4),
            'train_acc': round(train_acc, 2),
            'val_loss': round(v_loss, 4),
            'val_acc': round(v_acc, 2)
        })

        # Save metadata
        meta = {
            'model_name': model_name,
            'classes': class_names,
            'best_val_acc': round(best_val_acc, 2),
            'epochs_completed': len(history),
            'training_time_sec': round(time.time() - t_start, 2),
            'history': history
        }
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(meta, f, indent=2)

        print(f" {ep:>6}  {train_loss:>11.4f}  {train_acc:>9.2f}%  {v_loss:>9.4f}  {v_acc:>8.2f}%  {status_str:>10}")

    print(f"\n Finished {extra_epochs} epochs for {model_name} in {time.time()-t_start:.1f}s.")
    print(f" Best Validation Accuracy: {best_val_acc:.2f}%\n")
    return best_val_acc

# ==============================================================================
# DATASET CURATION & BALANCING
# ==============================================================================
def curate_chest_dataset():
    covid_root = os.path.join(DS_DIR, "COVID-19_Radiography_Dataset")
    tb_root = os.path.join(DS_DIR, "TB_Chest_Radiography_Database")
    cxr_root = os.path.join(DS_DIR, "chest_xray")

    # Class 0: COVID-19
    covid_pool = collect_images_from_dir(os.path.join(covid_root, "COVID", "images"), 0)
    # Class 1: Normal
    norm_pool = (
        collect_images_from_dir(os.path.join(covid_root, "Normal", "images"), 1) +
        collect_images_from_dir(os.path.join(tb_root, "Normal"), 1) +
        collect_images_from_dir(os.path.join(cxr_root, "train", "NORMAL"), 1)
    )
    # Class 2: Pneumonia
    pneu_pool = (
        collect_images_from_dir(os.path.join(covid_root, "Viral Pneumonia", "images"), 2) +
        collect_images_from_dir(os.path.join(cxr_root, "train", "PNEUMONIA"), 2)
    )
    # Class 3: Tuberculosis
    tb_pool = collect_images_from_dir(os.path.join(tb_root, "Tuberculosis"), 3)

    random.shuffle(covid_pool)
    random.shuffle(norm_pool)
    random.shuffle(pneu_pool)
    random.shuffle(tb_pool)

    # Balanced per-class distribution: 350 train / 75 val per class
    N_TR, N_VA = 350, 75
    train_items = (
        covid_pool[:N_TR] +
        norm_pool[:N_TR] +
        pneu_pool[:N_TR] +
        tb_pool[:N_TR]
    )
    val_items = (
        covid_pool[N_TR:N_TR+N_VA] +
        norm_pool[N_TR:N_TR+N_VA] +
        pneu_pool[N_TR:N_TR+N_VA] +
        tb_pool[N_TR:N_TR+N_VA]
    )

    random.shuffle(train_items)
    random.shuffle(val_items)
    return train_items, val_items

def curate_bone_dataset():
    bone_root = os.path.join(DS_DIR, "Bone_Fracture_Binary_Classification", "Bone_Fracture_Binary_Classification")
    
    # Class 0: Fracture
    frac_pool = (
        collect_images_from_dir(os.path.join(bone_root, "train", "fractured"), 0) +
        collect_images_from_dir(os.path.join(bone_root, "test", "fractured"), 0)
    )
    # Class 1: Normal
    norm_pool = (
        collect_images_from_dir(os.path.join(bone_root, "train", "not fractured"), 1) +
        collect_images_from_dir(os.path.join(bone_root, "test", "not fractured"), 1)
    )

    random.shuffle(frac_pool)
    random.shuffle(norm_pool)

    # 450 train / 100 val per class
    N_TR, N_VA = 450, 100
    train_items = frac_pool[:N_TR] + norm_pool[:N_TR]
    val_items = frac_pool[N_TR:N_TR+N_VA] + norm_pool[N_TR:N_TR+N_VA]

    random.shuffle(train_items)
    random.shuffle(val_items)
    return train_items, val_items

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == '__main__':
    t_pipeline = time.time()

    # 1. Chest ResNet-18
    print("\n[1/2] Curating balanced multi-disease Chest dataset...")
    chest_train, chest_val = curate_chest_dataset()
    chest_acc = train_network(
        model_name="chest_resnet18",
        num_classes=4,
        class_names=['COVID-19', 'Normal', 'Pneumonia', 'Tuberculosis'],
        train_items=chest_train,
        val_items=chest_val,
        extra_epochs=2
    )

    # 2. Bone Fracture ResNet-18
    print("\n[2/2] Curating balanced Bone Fracture dataset...")
    bone_train, bone_val = curate_bone_dataset()
    bone_acc = train_network(
        model_name="bone_resnet18",
        num_classes=2,
        class_names=['Fracture', 'Normal'],
        train_items=bone_train,
        val_items=bone_val,
        extra_epochs=2
    )

    print("\n" + "=" * 65)
    print(" 🎉 TRAINING CYCLE COMPLETE!")
    print(f" Chest ResNet-18 (4-Class):  Val Accuracy = {chest_acc:.2f}%")
    print(f" Bone ResNet-18 (Binary):    Val Accuracy = {bone_acc:.2f}%")
    print(f" Total Cycle Time:           {(time.time()-t_pipeline)/60:.2f} minutes")
    print(" Weights saved in: models/weights/chest_resnet18.pth, bone_resnet18.pth")
    print("=" * 65 + "\n")
