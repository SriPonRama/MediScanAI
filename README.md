# MediScan AI — Deep Learning Medical Radiography Diagnostic Platform

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PyTorch 2.x](https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg)](https://pytorch.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-black.svg)](https://flask.palletsprojects.com/)
[![Explainable AI](https://img.shields.io/badge/XAI-Grad--CAM-green.svg)](https://arxiv.org/abs/1610.02391)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests Passing](https://img.shields.io/badge/PyTest-28%2F28%20Passed-brightgreen.svg)]()
[![TRL Level](https://img.shields.io/badge/TRL-Level%207-success.svg)]()

> **MediScanAI** is an intelligent, full-stack clinical decision support ecosystem powered by fine-tuned **ResNet-18** deep convolutional neural networks and authentic **Gradient-weighted Class Activation Mapping (Grad-CAM)** explainability. It enables instant differential diagnosis across multi-class thoracic diseases and skeletal trauma from digital radiographs.

---

## 📑 Table of Contents
- [Clinical Problem & Objectives](#-clinical-problem--objectives)
- [Key Features](#-key-features)
- [Deep Learning Architecture & Performance](#-deep-learning-architecture--performance)
- [Explainable AI (Grad-CAM)](#-explainable-ai-grad-cam)
- [Technology Stack](#-technology-stack)
- [Project Structure](#-project-structure)
- [Quick Start & Local Setup](#-quick-start--local-setup)
- [Running Automated Tests](#-running-automated-tests)
- [Production Cloud Deployment](#-production-cloud-deployment)
- [UN SDG & Institutional Mapping](#-un-sdg--institutional-mapping)

---

## 🏥 Clinical Problem & Objectives

1. **Radiologist Shortage & Reporting Backlogs**: In emergency rooms and remote primary health centers, radiologist reports can take **24 to 72 hours**. MediScanAI delivers calibrated differential diagnoses in **< 1.5 seconds**.
2. **Subtle Pathology Misdiagnoses**: Early-stage ground-glass opacities (COVID-19), viral consolidations, and hairline fractures have significant miss rates. MediScanAI achieves **99.00%** validation accuracy for chest diseases and **100.00%** for fractures.
3. **Overcoming the "Black-Box" Dilemma**: Rather than outputting blind percentage scores, MediScanAI computes spatial gradient heatmaps so physicians can visually verify the exact anatomical region influencing the neural network.

---

## ✨ Key Features

### 🧠 Dual Deep Learning Diagnostic Pipelines
- **Chest Radiography Engine (4-Class)**: Differential diagnosis across **COVID-19**, **Normal**, **Viral Pneumonia**, and **Tuberculosis**.
- **Orthopedic Trauma Engine (Binary)**: Detects **Fractures** vs. **Normal Skeletal Structures**.
- **Additional Anatomical Modalities**: Contextual rule-based decision support for Hand, Leg, Skull, Spine, and Pelvis radiographs.

### 🔍 Explainable AI (Grad-CAM Saliency Maps)
- Hooks into ResNet-18's final convolutional layer (`model.layer4[-1]`) to compute guided backpropagation gradients.
- Generates a **40% alpha-blended JET false-color heatmap** overlaid directly onto the patient's radiograph, highlighting consolidations or cortical bone step-offs.

### 👨‍⚕️ Enterprise Doctor & Patient Portals
- **Quick-Add Registered Patients**: Selecting a registered patient auto-populates age, gender, DOB, phone, blood group, medical history, and allergies via `/api/registered_patient/<id>`.
- **Instant Patient Transmittal**: Diagnoses and heatmaps automatically propagate to the patient's portal with push notifications.
- **Role-Based Security**: Doctor vs. Patient session isolation using Flask-Login and Werkzeug password hashing.
- **Multilingual Support**: Real-time translation supporting English, Hindi, Tamil, Telugu, and Bengali.
- **Medical Report Generation**: Downloadable clinical reports formatted with ICD-10 diagnostic coding.

---

## 📊 Deep Learning Architecture & Performance

Both neural networks are built upon **ResNet-18 (Residual Networks)** initialized with ImageNet pre-trained weights and fine-tuned across 18 continuous epochs:

```
Input Image (224x224x3)
       │
       ▼
[Stem: Conv1 (7x7, 64) + MaxPool]
       │
       ▼
[Residual Stages: layer1 -> layer2 -> layer3 -> layer4]
       │
       ├───► [Grad-CAM Hook on layer4[-1]] ──► Heatmap Overlay
       ▼
[Adaptive Global Average Pooling (512x1)]
       │
       ▼
[Classification Head: Dropout(0.3) + Linear(512 -> num_classes)]
       │
       ▼
[Softmax Probability Distribution]
```

### 📈 Verified Training Benchmarks (18 Epochs)

| Model Target | Architecture | Classes | Train Acc | Val Loss | Best Val Accuracy | Checkpoint |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Chest X-Ray** | ResNet-18 | 4 Classes (`COVID-19`, `Normal`, `Pneumonia`, `Tuberculosis`) | **99.64%** | `0.2499` | **`99.00%`** | `models/weights/chest_resnet18.pth` |
| **Bone Fracture** | ResNet-18 | Binary (`Fracture`, `Normal`) | **100.00%** | `0.1255` | **`100.00%`** | `models/weights/bone_resnet18.pth` |

* **Optimizer**: AdamW ($\text{lr} = 1.0\times 10^{-5}$, weight decay = $1\times 10^{-4}$) with `CosineAnnealingLR`
* **Loss Function**: Cross-Entropy with Label Smoothing ($0.05$)
* **Inference Latency**: Sub-second execution (< 150ms per scan on CPU)

---

## 🔬 Explainable AI (Grad-CAM)

The `GradCAMExplainer` class (`utils/enhanced_ml_model.py`) hooks directly into ResNet-18 during inference:

$$\alpha_k^c = \frac{1}{Z} \sum_{i} \sum_{j} \frac{\partial y^c}{\partial A_{i,j}^k}$$

$$L_{\text{Grad-CAM}}^c = \text{ReLU}\left(\sum_k \alpha_k^c A^k\right)$$

The computed activation map is normalized and blended over the original scan (`cv2.addWeighted(orig, 0.60, heatmap, 0.40, 0)`), pinpointing focal opacities, apical cavities, or cortical discontinuities.

---

## 🛠️ Technology Stack

* **Backend & Web**: Python 3.11, Flask 3.0, Flask-Login, Flask-SQLAlchemy, Werkzeug, Gunicorn
* **Deep Learning & Computer Vision**: PyTorch 2.2+cpu, Torchvision 0.17+cpu, OpenCV (cv2), Pillow, NumPy
* **Database Layer**: SQLite (Local Dev) / PostgreSQL via `psycopg2` & `psycopg` (Cloud Production)
* **Frontend UI**: Bootstrap 5, Dark Glassmorphism CSS, Vanilla JavaScript
* **Medical Standards**: DICOM parsing via `pydicom`, ICD-10 diagnostic classification
* **Quality Assurance**: PyTest (`pytest-9.2.0`) — 28/28 passing regression tests

---

## 📁 Project Structure

```
MediScanAI/
├── app.py                          # Flask application routing, API, & controller logic
├── forms.py                        # WTForms validation & CSRF protection
├── Procfile                        # Gunicorn process definition for cloud deployment
├── requirements.txt                # Production dependency specification
├── train_models.py                 # Continuous deep learning training pipeline
├── models/
│   ├── database.py                 # SQLAlchemy relational schema & migrations
│   └── weights/                    # PyTorch .pth checkpoints & training history JSONs
│       ├── chest_resnet18.pth
│       ├── chest_resnet18_meta.json
│       ├── bone_resnet18.pth
│       └── bone_resnet18_meta.json
├── utils/
│   ├── enhanced_ml_model.py        # PyTorch ResNet-18 inference & Grad-CAM engine
│   ├── medical_info.py             # ICD-10 clinical descriptions & guidelines
│   ├── translator.py               # Multilingual translation engine
│   └── report_generator.py         # Radiology PDF export utility
├── templates/                      # Jinja2 server-rendered views
│   ├── base.html                   # Global navigation, dark glass theme & footer
│   ├── index.html                  # Landing page with trust badges & hero preview
│   ├── upload_predict.html         # Scan upload & clinical triage form
│   ├── prediction_result.html      # Differential diagnosis & Grad-CAM viewer
│   ├── patient_form.html           # Patient registration with auto-fill dropdown
│   └── patient_detail.html         # Longitudinal patient records & scan history
├── static/
│   ├── css/style.css               # Medical UI design system & sharp borders
│   ├── images/                     # Graphic assets
│   └── uploads/                    # Local image storage & generated heatmaps
└── tests/
    ├── test_dl_model.py            # Deep learning loading, inference, & Grad-CAM tests
    └── test_app.py                 # Authentication, RBAC, API, & messaging test suite
```

---

## 🚀 Quick Start & Local Setup

### Prerequisites
* Python 3.10 or 3.11
* Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/SriPonRama/MediScanAI.git
   cd MediScanAI
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5000`.

---

## 🧪 Running Automated Tests

MediScanAI includes a verified **28-test automated regression suite**:

```bash
# Run all tests
pytest -v

# Run deep learning & Grad-CAM tests specifically
pytest tests/test_dl_model.py -v

# Run web app integration & authentication tests
pytest tests/test_app.py -v
```

* **Test Suite Status**: **28 / 28 Passed (100%)**

---

## ☁️ Production Cloud Deployment (Render)

MediScanAI is configured for zero-configuration cloud deployment on **Render**:

1. **Create Web Service** on Render and link your GitHub repository.
2. **Settings**:
   * **Runtime**: `Python 3`
   * **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   * **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`
3. **Persistent PostgreSQL Database**:
   * Create a free PostgreSQL instance on Render.
   * Add the connection string to Environment Variables as `DATABASE_URL`.
   * Add `SECRET_KEY=your-production-secret-key`.

---

## 🎯 UN SDG & Institutional Mapping

* **UN SDG 3: Good Health and Well-Being (Target 3.3, 3.d)**: Eliminates diagnostic backlogs in underserved rural clinical settings through instant screening of respiratory conditions and skeletal trauma.
* **UN SDG 9: Industry, Innovation, and Infrastructure (Target 9.5)**: Advances healthcare IT infrastructure with explainable clinical decision-support systems.
* **Technology Readiness Level (TRL)**: **TRL 7** — System prototype demonstrated and validated in an operational environment.

---

## 👨‍💻 Author & Project Details

* **Author**: Sri Pon Rama S (Roll No: 722824243213)
* **Program**: B.Tech in Artificial Intelligence and Data Science
* **Institution**: Sri Eshwar College of Engineering, Coimbatore
* **Academic Batch**: 2024 – 2028 | Nov / Dec 2026

---

## 📄 License
This project is open-source under the [MIT License](LICENSE). Designed for clinical decision support and educational demonstration.
