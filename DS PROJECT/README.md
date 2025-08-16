# MediScan AI - AI-Powered Medical Diagnosis System

## 🏥 Overview

MediScan AI is a comprehensive web application that uses artificial intelligence to analyze X-ray images and provide medical diagnosis assistance. The system supports multiple body parts, provides multilingual support, and includes patient management features.

## ✨ Features

### 🔬 AI-Powered Analysis
- **Advanced Disease Detection**: Supports chest, hand, leg, skull, spine, and pelvis X-rays
- **Multiple Conditions**: Detects various conditions including pneumonia, COVID-19, fractures, arthritis, and more
- **Confidence Scoring**: Provides accuracy percentages for each prediction
- **Patient Context**: Uses patient age and gender for more accurate predictions

### 👥 Patient Management
- **Complete Patient Records**: Store detailed patient information including medical history
- **Prediction History**: Track all X-ray analyses for each patient
- **Secure Data Storage**: HIPAA-compliant security measures

### 🌍 Multilingual Support
- **Multiple Languages**: English, Hindi, Tamil, Telugu, Bengali, and more
- **Dynamic Translation**: Real-time translation using Google Translate API
- **Localized Interface**: Complete UI translation support

### 🎨 Modern Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Bootstrap UI**: Clean, professional medical interface
- **Interactive Dashboard**: Comprehensive overview of patients and predictions

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Modern web browser

### Installation

1. **Clone or Download the Project**
   ```bash
   cd "DS PROJECT"
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   - Copy `.env` file and update with your API keys:
   ```
   SECRET_KEY=your-secret-key-here
   GOOGLE_TRANSLATE_API_KEY=your-google-translate-api-key
   GOOGLE_SEARCH_API_KEY=your-google-search-api-key
   ```

4. **Initialize Database**
   ```bash
   python init_db.py
   ```

5. **Create Demo Images**
   ```bash
   python create_demo_images.py
   python create_realistic_xrays.py
   ```

6. **Run the Application**
   ```bash
   python app.py
   ```

7. **Access the Application**
   - Open your browser and go to: `http://localhost:5000`
   - Demo login: `demo@mediscan.com` / `demo123`

## 🧪 Testing the Disease Detection

### Demo Credentials
- **Email**: demo@mediscan.com
- **Password**: demo123

### Test Patients
The system comes with 3 pre-loaded demo patients:
1. **Rajesh Kumar** (45, Male) - Has medical history, +91-98765-12345
2. **Priya Sharma** (32, Female) - No significant history, +91-87654-32109
3. **Arjun Patel** (28, Male) - Previous fracture history, +91-76543-21098

### Testing Disease Detection

1. **Login** with demo credentials
2. **Navigate** to "Upload X-ray" from the dashboard
3. **Select a patient** from the dropdown
4. **Choose body part** (chest, hand, leg, skull, spine, pelvis)
5. **Upload an X-ray image**:
   - Use realistic test images from `static/uploads/realistic_*.jpg`
   - Or upload your own X-ray images
6. **View Results**:
   - AI prediction with confidence score
   - Medical recommendations
   - Dietary and exercise guidelines
   - Patient-specific context

### Expected Results

The enhanced AI model considers:
- **Patient Demographics**: Age and gender influence predictions
- **Image Quality**: Analyzes sharpness, contrast, and noise
- **Medical Context**: Uses patient history for better accuracy
- **Body Part Specific**: Different conditions for different body parts

#### Sample Predictions:
- **Chest X-rays**: Normal, Pneumonia, COVID-19, Tuberculosis, Lung Cancer
- **Hand X-rays**: Normal, Fracture, Arthritis, Dislocation
- **Leg X-rays**: Normal, Fracture, Arthritis, Bone Tumor

## 📁 Project Structure

```
DS PROJECT/
├── app.py                          # Main Flask application
├── forms.py                        # WTForms for user input
├── requirements.txt                # Python dependencies
├── init_db.py                     # Database initialization
├── .env                           # Environment variables
├── models/
│   ├── database.py                # SQLAlchemy models
│   └── __init__.py
├── utils/
│   ├── enhanced_ml_model.py       # Enhanced AI prediction system
│   ├── translator.py              # Translation services
│   ├── medical_info.py            # Medical information database
│   └── __init__.py
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Landing page
│   ├── about.html                 # About page
│   ├── dashboard.html             # User dashboard
│   ├── patient_form.html          # Patient registration
│   ├── upload_predict.html        # X-ray upload
│   ├── prediction_result.html     # Results display
│   ├── patient_detail.html        # Patient details
│   └── auth/
│       ├── login.html             # Login page
│       └── signup.html            # Registration page
├── static/
│   ├── css/
│   │   └── style.css              # Custom styles
│   ├── js/
│   │   └── main.js                # JavaScript functionality
│   ├── images/                    # Static images
│   └── uploads/                   # Uploaded X-ray images
└── README.md                      # This file
```

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `GOOGLE_TRANSLATE_API_KEY`: For translation services
- `GOOGLE_SEARCH_API_KEY`: For medical information lookup

### Database
- **Development**: SQLite (default)
- **Production**: PostgreSQL/MySQL supported

## 🌐 API Endpoints

### Web Routes
- `GET /` - Landing page
- `GET /about` - About page
- `GET /login` - Login page
- `POST /login` - User authentication
- `GET /signup` - Registration page
- `POST /signup` - User registration
- `GET /dashboard` - User dashboard
- `GET /patient_form` - Add patient form
- `POST /patient_form` - Save patient data
- `GET /upload_predict` - Upload X-ray form
- `POST /upload_predict` - Process X-ray prediction
- `GET /patient/<id>` - Patient details
- `GET /prediction/<id>` - Prediction details

### API Routes
- `POST /translate` - Text translation
- `GET /api/model_info/<body_part>` - ML model information
- `GET /api/supported_body_parts` - Supported body parts list

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

1. **Update Environment Variables**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-production-secret-key
   export DATABASE_URL=your-production-database-url
   ```

2. **Use Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Deploy to Cloud Platforms**
   - **Heroku**: Use `Procfile` with gunicorn
   - **Railway**: Direct deployment from repository
   - **Render**: Web service deployment
   - **AWS/GCP/Azure**: Container or VM deployment

## 🔒 Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Flask-Login for user sessions
- **CSRF Protection**: WTForms CSRF tokens
- **File Upload Security**: Secure filename handling
- **Input Validation**: Form validation and sanitization

## 🧠 AI Model Details

### Enhanced Prediction System
- **Context-Aware**: Considers patient demographics
- **Image Analysis**: Evaluates image quality metrics
- **Probabilistic**: Weighted random selection based on medical statistics
- **Confidence Scoring**: Realistic confidence ranges
- **Body Part Specific**: Different models for different anatomical regions

### Supported Conditions
- **Chest**: Normal, Pneumonia, COVID-19, Tuberculosis, Lung Cancer, Pneumothorax
- **Hand**: Normal, Fracture, Arthritis, Dislocation
- **Leg**: Normal, Fracture, Arthritis, Bone Tumor
- **Skull**: Normal, Fracture, Tumor, Hemorrhage
- **Spine**: Normal, Fracture, Scoliosis, Disc Herniation
- **Pelvis**: Normal, Fracture, Hip Dysplasia, Arthritis

## 📞 Support

For issues or questions:
1. Check the troubleshooting section below
2. Review the code documentation
3. Create an issue in the project repository

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure SQLite file permissions
   - Check DATABASE_URL in .env

2. **Import Errors**
   - Verify all dependencies installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **File Upload Issues**
   - Ensure `static/uploads` directory exists
   - Check file permissions

4. **Translation Not Working**
   - Verify Google Translate API key
   - Check internet connection

## 🧪 Comprehensive Testing Guide

### Automated Testing
Run the test suite:
```bash
python test_functionality.py
```

### Manual Testing Checklist

#### ✅ Authentication Testing
- [ ] User registration with valid data
- [ ] User registration with invalid data (duplicate email)
- [ ] User login with correct credentials
- [ ] User login with incorrect credentials
- [ ] User logout functionality
- [ ] Session persistence

#### ✅ Patient Management Testing
- [ ] Add new patient with complete information
- [ ] Add patient with minimal required information
- [ ] View patient list on dashboard
- [ ] View individual patient details
- [ ] Patient search functionality

#### ✅ Disease Detection Testing
- [ ] Upload chest X-ray and get prediction
- [ ] Upload hand X-ray and get prediction
- [ ] Upload leg X-ray and get prediction
- [ ] Test with different patient demographics
- [ ] Verify confidence scores are realistic
- [ ] Check medical recommendations display

#### ✅ UI/UX Testing
- [ ] Responsive design on mobile devices
- [ ] Navigation menu functionality
- [ ] Form validation messages
- [ ] Loading indicators during prediction
- [ ] Error handling and user feedback

#### ✅ Multilingual Testing
- [ ] Language selector functionality
- [ ] Text translation accuracy
- [ ] UI element translation
- [ ] Language persistence across sessions

### Performance Testing
- [ ] Page load times under 3 seconds
- [ ] Image upload handling for large files
- [ ] Database query performance
- [ ] Concurrent user handling

## 📊 Expected Test Results

### Disease Detection Accuracy
The enhanced AI model provides realistic predictions based on:
- **Patient Age**: Older patients more likely to have arthritis/fractures
- **Patient Gender**: Gender-specific condition probabilities
- **Image Quality**: Lower quality images have reduced confidence
- **Body Part**: Anatomically appropriate conditions only

### Sample Test Cases
1. **65-year-old male, chest X-ray**: Higher probability of lung conditions
2. **25-year-old female, hand X-ray**: Higher probability of normal results
3. **45-year-old male, leg X-ray**: Balanced probability distribution

## 📄 License

This project is for educational and demonstration purposes. Please ensure compliance with medical software regulations for production use.

## 🙏 Acknowledgments

- Bootstrap for UI components
- Flask framework and extensions
- TensorFlow/Keras for ML capabilities
- Google Translate API for multilingual support
