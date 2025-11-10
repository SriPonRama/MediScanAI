// Main JavaScript for MediScan AI

// Global variables
let currentLanguage = 'en';
let translations = {};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadTranslations().then(() => {
        // Apply saved language after translations are loaded
        if (currentLanguage !== 'en') {
            translatePage();
        }
    });
    setupEventListeners();
});

// Initialize application
function initializeApp() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Get current language from localStorage
    const savedLanguage = localStorage.getItem('mediscan_language');
    if (savedLanguage) {
        currentLanguage = savedLanguage;
        updateLanguageDisplay();
    }
}

// Setup event listeners
function setupEventListeners() {
    // File upload drag and drop
    const uploadArea = document.querySelector('.upload-area');
    if (uploadArea) {
        setupFileUpload(uploadArea);
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
    
    // Image preview
    const imageInputs = document.querySelectorAll('input[type="file"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', handleImagePreview);
    });
}

// File upload functionality
function setupFileUpload(uploadArea) {
    const fileInput = uploadArea.querySelector('input[type="file"]');
    
    // Drag and drop events
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleImagePreview({ target: fileInput });
        }
    });
    
    // Click to upload
    uploadArea.addEventListener('click', function() {
        fileInput.click();
    });
}

// Handle image preview
function handleImagePreview(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            // Create or update image preview
            let preview = document.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview mt-3';
                event.target.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <div class="card">
                    <img src="${e.target.result}" class="card-img-top" style="max-height: 300px; object-fit: contain;">
                    <div class="card-body">
                        <h6 class="card-title">${file.name}</h6>
                        <p class="card-text small text-muted">Size: ${formatFileSize(file.size)}</p>
                    </div>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Handle form submission
function handleFormSubmit(event) {
    const form = event.target;
    
    // Show loading spinner for prediction forms
    if (form.classList.contains('prediction-form')) {
        showLoadingSpinner();
    }
    
    // Validate required fields
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('is-invalid');
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    if (!isValid) {
        event.preventDefault();
        hideLoadingSpinner();
        showAlert('Please fill in all required fields.', 'error');
    }
}

// Language functionality
function changeLanguage(langCode) {
    currentLanguage = langCode;
    localStorage.setItem('mediscan_language', langCode);
    updateLanguageDisplay();
    translatePage();
}

function updateLanguageDisplay() {
    const currentLangElement = document.getElementById('currentLanguage');
    const languages = {
        'en': 'English',
        'hi': 'हिंदी',
        'ta': 'தமிழ்',
        'te': 'తెలుగు',
        'bn': 'বাংলা'
    };
    
    if (currentLangElement) {
        currentLangElement.textContent = languages[currentLanguage] || 'English';
    }
}

// Load translations
async function loadTranslations() {
    try {
        translations = {
            'en': {
                'hero-title': 'AI for Smarter Disease Detection',
                'hero-subtitle': 'Advanced X-ray analysis powered by artificial intelligence to help healthcare professionals make faster, more accurate diagnoses.',
                'features-title': 'Why Choose MediScan AI?',
                'login-title': 'Welcome Back',
                'signup-title': 'Create Account',
                'dashboard': 'Dashboard',
                'add-patient': 'Add Patient',
                'upload-xray': 'Upload X-ray',
                'patients': 'Patients',
                'recent-predictions': 'Recent Predictions',
                'name': 'Name',
                'age': 'Age',
                'gender': 'Gender',
                'contact': 'Contact',
                'view-details': 'View Details'
            },
            'hi': {
                'hero-title': 'स्मार्ट रोग निदान के लिए AI',
                'hero-subtitle': 'कृत्रिम बुद्धिमत्ता द्वारा संचालित उन्नत एक्स-रे विश्लेषण',
                'features-title': 'MediScan AI क्यों चुनें?',
                'login-title': 'वापस स्वागत है',
                'signup-title': 'खाता बनाएं',
                'dashboard': 'डैशबोर्ड',
                'add-patient': 'मरीज़ जोड़ें',
                'upload-xray': 'एक्स-रे अपलोड करें',
                'patients': 'मरीज़',
                'recent-predictions': 'हाल की भविष्यवाणियां',
                'name': 'नाम',
                'age': 'उम्र',
                'gender': 'लिंग',
                'contact': 'संपर्क',
                'view-details': 'विवरण देखें',
                'welcome-back': 'वापस स्वागत है',
                'total-patients': 'कुल मरीज़',
                'recent-scans': 'हाल के स्कैन',
                'normal-results': 'सामान्य परिणाम',
                'requires-attention': 'ध्यान देने की जरूरत'
            },
            'ta': {
                'hero-title': 'ஸ்மார்ட் நோய் கண்டறிதலுக்கான AI',
                'hero-subtitle': 'செயற்கை நுண்ணறிவால் இயக்கப்படும் மேம்பட்ட எக்ஸ்-ரே பகுப்பாய்வு',
                'features-title': 'MediScan AI ஏன் தேர்வு செய்ய வேண்டும்?',
                'login-title': 'மீண்டும் வரவேற்கிறோம்',
                'signup-title': 'கணக்கு உருவாக்கவும்',
                'dashboard': 'டாஷ்போர்டு',
                'add-patient': 'நோயாளியைச் சேர்க்கவும்',
                'upload-xray': 'எக்ஸ்-ரே பதிவேற்றவும்',
                'patients': 'நோயாளிகள்',
                'recent-predictions': 'சமீபத்திய கணிப்புகள்',
                'name': 'பெயர்',
                'age': 'வயது',
                'gender': 'பாலினம்',
                'contact': 'தொடர்பு',
                'view-details': 'விவரங்களைப் பார்க்கவும்'
            },
            'te': {
                'hero-title': 'స్మార్ట్ వ్యాధి నిర్ధారణ కోసం AI',
                'hero-subtitle': 'కృత్రిమ మేధస్సుతో నడిచే అధునాతన ఎక్స్-రే విశ్లేషణ',
                'features-title': 'MediScan AI ఎందుకు ఎంచుకోవాలి?',
                'login-title': 'తిరిగి స్వాగతం',
                'signup-title': 'ఖాతా సృష్టించండి',
                'dashboard': 'డాష్‌బోర్డ్',
                'add-patient': 'రోగిని జోడించండి',
                'upload-xray': 'ఎక్స్-రే అప్‌లోడ్ చేయండి',
                'patients': 'రోగులు',
                'recent-predictions': 'ఇటీవలి అంచనాలు',
                'name': 'పేరు',
                'age': 'వయస్సు',
                'gender': 'లింగం',
                'contact': 'సంప్రదింపు',
                'view-details': 'వివరాలు చూడండి'
            },
            'bn': {
                'hero-title': 'স্মার্ট রোগ নির্ণয়ের জন্য AI',
                'hero-subtitle': 'কৃত্রিম বুদ্ধিমত্তা দ্বারা চালিত উন্নত এক্স-রে বিশ্লেষণ',
                'features-title': 'কেন MediScan AI বেছে নেবেন?',
                'login-title': 'আবার স্বাগতম',
                'signup-title': 'অ্যাকাউন্ট তৈরি করুন',
                'dashboard': 'ড্যাশবোর্ড',
                'add-patient': 'রোগী যোগ করুন',
                'upload-xray': 'এক্স-রে আপলোড করুন',
                'patients': 'রোগীরা',
                'recent-predictions': 'সাম্প্রতিক পূর্বাভাস',
                'name': 'নাম',
                'age': 'বয়স',
                'gender': 'লিঙ্গ',
                'contact': 'যোগাযোগ',
                'view-details': 'বিস্তারিত দেখুন'
            }
        };
    } catch (error) {
        console.error('Error loading translations:', error);
    }
}

// Translate page content
function translatePage() {
    if (currentLanguage === 'en') {
        // Reset to original English text
        location.reload();
        return;
    }
    
    // Translate elements with data-translate attribute
    const elementsToTranslate = document.querySelectorAll('[data-translate]');
    elementsToTranslate.forEach(element => {
        const key = element.getAttribute('data-translate');
        const translation = translations[currentLanguage]?.[key];
        if (translation) {
            element.textContent = translation;
        }
    });
    
    // Translate common text elements
    translateCommonElements();
}

// Translate common elements without data-translate attributes
function translateCommonElements() {
    const textMappings = {
        'Dashboard': translations[currentLanguage]?.['dashboard'],
        'Add Patient': translations[currentLanguage]?.['add-patient'],
        'Upload X-ray': translations[currentLanguage]?.['upload-xray'],
        'Patients': translations[currentLanguage]?.['patients'],
        'Recent Predictions': translations[currentLanguage]?.['recent-predictions'],
        'Name': translations[currentLanguage]?.['name'],
        'Age': translations[currentLanguage]?.['age'],
        'Gender': translations[currentLanguage]?.['gender'],
        'Contact': translations[currentLanguage]?.['contact'],
        'View Details': translations[currentLanguage]?.['view-details'],
        'Your Patients': translations[currentLanguage]?.['patients'],
        'Welcome back': translations[currentLanguage]?.['welcome-back'] || 'Welcome back',
        'Total Patients': translations[currentLanguage]?.['total-patients'] || 'Total Patients',
        'Recent Scans': translations[currentLanguage]?.['recent-scans'] || 'Recent Scans',
        'Normal Results': translations[currentLanguage]?.['normal-results'] || 'Normal Results',
        'Requires Attention': translations[currentLanguage]?.['requires-attention'] || 'Requires Attention'
    };
    
    // Find and replace text in navigation and common elements
    document.querySelectorAll('a, button, h1, h2, h3, h4, h5, h6, th, td, label, span').forEach(element => {
        const text = element.textContent.trim();
        if (textMappings[text]) {
            element.textContent = textMappings[text];
        }
    });
    
    // Translate medical terms in prediction results
    translateMedicalTerms();
}

// Translate medical terms using backend API
async function translateMedicalTerms() {
    if (currentLanguage === 'en') return;
    
    const medicalTerms = document.querySelectorAll('.prediction-result, .medical-term');
    
    for (const element of medicalTerms) {
        const text = element.textContent.trim();
        if (text && ['Normal', 'Pneumonia', 'COVID-19', 'Fracture', 'Arthritis', 'Tuberculosis', 'Lung Cancer', 'Dislocation', 'Bone Tumor'].includes(text)) {
            try {
                const response = await fetch('/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        target_language: currentLanguage
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    element.textContent = data.translated_text;
                }
            } catch (error) {
                console.error('Translation error:', error);
            }
        }
    }
}

// Utility functions
function showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-overlay';
    spinner.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(spinner);
}

function hideLoadingSpinner() {
    const spinner = document.querySelector('.loading-overlay');
    if (spinner) {
        spinner.remove();
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// Prediction result animation
function animatePredictionResult() {
    const resultCard = document.querySelector('.prediction-card');
    if (resultCard) {
        resultCard.classList.add('slide-up');
    }
    
    // Animate confidence bar
    const confidenceBar = document.querySelector('.confidence-indicator');
    if (confidenceBar) {
        const confidence = parseFloat(confidenceBar.dataset.confidence || 0);
        confidenceBar.style.width = '0%';
        
        setTimeout(() => {
            confidenceBar.style.transition = 'width 2s ease-in-out';
            confidenceBar.style.width = confidence + '%';
        }, 500);
    }
}

// Patient search functionality
function searchPatients() {
    const searchInput = document.getElementById('patientSearch');
    const patientCards = document.querySelectorAll('.patient-card');
    
    if (!searchInput) return;
    
    const searchTerm = searchInput.value.toLowerCase();
    
    patientCards.forEach(card => {
        const patientName = card.querySelector('.patient-name')?.textContent.toLowerCase() || '';
        const patientInfo = card.textContent.toLowerCase();
        
        if (patientInfo.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Export functions for global use
window.changeLanguage = changeLanguage;
window.showLoadingSpinner = showLoadingSpinner;
window.hideLoadingSpinner = hideLoadingSpinner;
window.showAlert = showAlert;
window.searchPatients = searchPatients;
