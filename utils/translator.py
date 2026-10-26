"""
MediScan AI - Multilingual Translation Service
Provides real-time translation with instantaneous local medical/UI dictionary caching
and Google Translate fallback for comprehensive dynamic multilingual web support.
"""

import os
import json
import atexit
import logging

logger = logging.getLogger(__name__)

# Supported languages with display metadata
SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'native': 'English', 'flag': '🇺🇸'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'flag': '🇮🇳'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'flag': '🇮🇳'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'flag': '🇮🇳'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'flag': '🇮🇳'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'flag': '🇮🇳'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'flag': '🇮🇳'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'flag': '🇮🇳'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'flag': '🇮🇳'},
    'es': {'name': 'Spanish', 'native': 'Español', 'flag': '🇪🇸'},
    'fr': {'name': 'French', 'native': 'Français', 'flag': '🇫🇷'},
    'de': {'name': 'German', 'native': 'Deutsch', 'flag': '🇩🇪'},
    'ar': {'name': 'Arabic', 'native': 'العربية', 'flag': '🇸🇦'}
}

# Curated high-performance dictionary for instant zero-latency UI translation
STATIC_DICTIONARY = {
    # Navigation & General UI
    'Home': {
        'hi': 'होम', 'ta': 'முகப்பு', 'te': 'హోమ్', 'bn': 'হোম',
        'mr': 'मुख्यपृष्ठ', 'gu': 'હોમ', 'kn': 'ಮುಖಪುಟ', 'ml': 'ഹോം',
        'es': 'Inicio', 'fr': 'Accueil', 'de': 'Startseite', 'ar': 'الرئيسية'
    },
    'About Us': {
        'hi': 'हमारे बारे में', 'ta': 'எங்களைப் பற்றி', 'te': 'మా గురించి', 'bn': 'আমাদের সম্পর্কে',
        'mr': 'आमच्याबद्दल', 'gu': 'અમારા વિશે', 'kn': 'ನಮ್ಮ ಬಗ್ಗೆ', 'ml': 'ഞങ്ങളെക്കുറിച്ച്',
        'es': 'Sobre Nosotros', 'fr': 'À propos', 'de': 'Über uns', 'ar': 'معلومات عنا'
    },
    'Dashboard': {
        'hi': 'डैशबोर्ड', 'ta': 'டாஷ்போர்டு', 'te': 'డాష్‌బోర్డ్', 'bn': 'ড্যাশবোর্ড',
        'mr': 'डॅशबोर्ड', 'gu': 'ડેશબોર્ડ', 'kn': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್', 'ml': 'ഡാഷ്‌ബോർഡ്',
        'es': 'Panel de Control', 'fr': 'Tableau de bord', 'de': 'Übersicht', 'ar': 'لوحة القيادة'
    },
    'Add Patient': {
        'hi': 'मरीज़ जोड़ें', 'ta': 'நோயாளியைச் சேர்க்கவும்', 'te': 'రోగిని జోడించండి', 'bn': 'রোগী যোগ করুন',
        'mr': 'रुग्ण जोडा', 'gu': 'દર્દી ઉમેરો', 'kn': 'ರೋಗಿಯನ್ನು ಸೇರಿಸಿ', 'ml': 'രോഗിയെ ചേർക്കുക',
        'es': 'Añadir Paciente', 'fr': 'Ajouter Patient', 'de': 'Patient hinzufügen', 'ar': 'إضافة مريض'
    },
    'Upload X-ray': {
        'hi': 'एक्स-रे अपलोड करें', 'ta': 'எக்ஸ்-ரே பதிவேற்றவும்', 'te': 'ఎక్స్-రే అప్‌లోడ్ చేయండి', 'bn': 'এক্স-রে আপলোড করুন',
        'mr': 'क्ष-किरण अपलोड करा', 'gu': 'એક્સ-રે અપલોડ કરો', 'kn': 'ಕ್ಷ-ಕಿರಣ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ', 'ml': 'എക്സ്-റേ അപ്‌ലോഡ് ചെയ്യുക',
        'es': 'Subir Radiografía', 'fr': 'Télécharger Radiographie', 'de': 'Röntgenbild hochladen', 'ar': 'تحميل الأشعة السينية'
    },
    'Login': {
        'hi': 'लॉग इन करें', 'ta': 'உள்நுழைக', 'te': 'లాగిన్', 'bn': 'লগ ইন করুন',
        'mr': 'लॉगिन', 'gu': 'લૉગિન', 'kn': 'ಲಾಗಿನ್', 'ml': 'ലോഗിൻ',
        'es': 'Iniciar Sesión', 'fr': 'Connexion', 'de': 'Anmelden', 'ar': 'تسجيل الدخول'
    },
    'Sign Up': {
        'hi': 'साइन अप करें', 'ta': 'பதிவுசெய்க', 'te': 'సైన్ అప్', 'bn': 'নিবন্ধন করুন',
        'mr': 'नोंदणी करा', 'gu': 'સાઇન અપ', 'kn': 'ಸೈನ್ ಅಪ್', 'ml': 'സൈൻ അപ്പ്',
        'es': 'Registrarse', 'fr': 'S\'inscrire', 'de': 'Registrieren', 'ar': 'إنشاء حساب'
    },
    'Logout': {
        'hi': 'लॉग आउट', 'ta': 'வெளியேறு', 'te': 'లాగ్ అవుట్', 'bn': 'লগ আউট',
        'mr': 'लॉग आउट', 'gu': 'લૉગ આઉટ', 'kn': 'ಲಾಗ್ ಔಟ್', 'ml': 'ലോഗ് ഔട്ട്',
        'es': 'Cerrar Sesión', 'fr': 'Déconnexion', 'de': 'Abmelden', 'ar': 'تسجيل الخروج'
    },
    'Language': {
        'hi': 'भाषा', 'ta': 'மொழி', 'te': 'భాష', 'bn': 'ভাষা',
        'mr': 'भाषा', 'gu': 'ભાષા', 'kn': 'ಭಾಷೆ', 'ml': 'ഭാഷ',
        'es': 'Idioma', 'fr': 'Langue', 'de': 'Sprache', 'ar': 'اللغة'
    },
    'Patients': {
        'hi': 'मरीज़', 'ta': 'நோயாளிகள்', 'te': 'రోగులు', 'bn': 'রোগীরা',
        'mr': 'रुग्ण', 'gu': 'દર્દીઓ', 'kn': 'ರೋಗಿಗಳು', 'ml': 'രോഗികൾ',
        'es': 'Pacientes', 'fr': 'Patients', 'de': 'Patienten', 'ar': 'المرضى'
    },
    'Your Patients': {
        'hi': 'आपके मरीज़', 'ta': 'உங்கள் நோயாளிகள்', 'te': 'మీ రోగులు', 'bn': 'আপনার রোগীরা',
        'mr': 'तुमचे रुग्ण', 'gu': 'તમારા દર્દીઓ', 'kn': 'ನಿಮ್ಮ ರೋಗಿಗಳು', 'ml': 'നിങ്ങളുടെ രോഗികൾ',
        'es': 'Sus Pacientes', 'fr': 'Vos Patients', 'de': 'Ihre Patienten', 'ar': 'مرضاك'
    },
    'Total Patients': {
        'hi': 'कुल मरीज़', 'ta': 'மொத்த நோயாளிகள்', 'te': 'మొత్తం రోగులు', 'bn': 'মোট রোগী',
        'mr': 'एकूण रुग्ण', 'gu': 'કુલ દર્દીઓ', 'kn': 'ಒಟ್ಟು ರೋಗಿಗಳು', 'ml': 'ആകെ രോഗികൾ',
        'es': 'Total de Pacientes', 'fr': 'Total Patients', 'de': 'Gesamtzahl Patienten', 'ar': 'إجمالي المرضى'
    },
    'Recent Scans': {
        'hi': 'हाल के स्कैन', 'ta': 'சமீபத்திய ஸ்கேன்கள்', 'te': 'ఇటీవలి స్కాన్లు', 'bn': 'সাম্প্রতিক স্ক্যান',
        'mr': 'अलीकडील स्कॅन', 'gu': 'તાજેતરના સ્કેન', 'kn': 'ಇತ್ತೀಚಿನ ಸ್ಕ್ಯಾನ್‌ಗಳು', 'ml': 'സമീപകാല സ്കാനുകൾ',
        'es': 'Escaneos Recientes', 'fr': 'Analyses Récentes', 'de': 'Aktuelle Scans', 'ar': 'الفحوصات الحديثة'
    },
    'Recent Predictions': {
        'hi': 'हाल के निदान', 'ta': 'சமீபத்திய கணிப்புகள்', 'te': 'ఇటీవలి అంచనాలు', 'bn': 'সাম্প্রতিক ফলাফল',
        'mr': 'अलीकडील अंदाज', 'gu': 'તાજેતરના અંદાજો', 'kn': 'ಇತ್ತೀಚಿನ ಮುನ್ಸೂಚನೆಗಳು', 'ml': 'സമീപകാല രോഗനിർണ്ണയം',
        'es': 'Diagnósticos Recientes', 'fr': 'Diagnostics Récents', 'de': 'Neueste Diagnosen', 'ar': 'التشخيصات الأخيرة'
    },
    'Normal Results': {
        'hi': 'सामान्य परिणाम', 'ta': 'இயல்பான முடிவுகள்', 'te': 'సాధారణ ఫలితాలు', 'bn': 'স্বাভাবিক ফলাফল',
        'mr': 'सामान्य निकाल', 'gu': 'સામાન્ય પરિણામો', 'kn': 'ಸಾಮಾನ್ಯ ಫಲಿತಾಂಶಗಳು', 'ml': 'സാധാരണ ഫലങ്ങൾ',
        'es': 'Resultados Normales', 'fr': 'Résultats Normaux', 'de': 'Normale Befunde', 'ar': 'نتائج طبيعية'
    },
    'Requires Attention': {
        'hi': 'ध्यान देने योग्य', 'ta': 'கவனம் தேவை', 'te': 'శ్రద్ధ అవసరం', 'bn': 'মনোযোগ প্রয়োজন',
        'mr': 'लक्ष देणे आवश्यक', 'gu': 'ધ્યાન આપવાની જરૂર છે', 'kn': 'ಗಮನ ಅಗತ್ಯವಿದೆ', 'ml': 'ശ്രദ്ധ ആവശ്യമാണ്',
        'es': 'Requiere Atención', 'fr': 'Nécessite Attention', 'de': 'Aufmerksamkeit erforderlich', 'ar': 'يتطلب اهتماماً'
    },
    'Welcome back': {
        'hi': 'वापस स्वागत है', 'ta': 'மீண்டும் வரவேற்கிறோம்', 'te': 'తిరిగి స్వాగతం', 'bn': 'আবার স্বাগতম',
        'mr': 'पुन्हा स्वागत आहे', 'gu': 'પાછા સ્વાગત છે', 'kn': 'ಮತ್ತೆ ಸ್ವಾಗತ', 'ml': 'വീണ്ടും സ്വാഗതം',
        'es': 'Bienvenido de nuevo', 'fr': 'Bon retour', 'de': 'Willkommen zurück', 'ar': 'مرحباً بعودتك'
    },
    'View Details': {
        'hi': 'विवरण देखें', 'ta': 'விவரங்களைக் காண்க', 'te': 'వివరాలు చూడండి', 'bn': 'বিস্তারিত দেখুন',
        'mr': 'तपशील पहा', 'gu': 'વિગતો જુઓ', 'kn': 'ವಿವರಗಳನ್ನು ವೀಕ್ಷಿಸಿ', 'ml': 'വിശദാംശങ്ങൾ കാണുക',
        'es': 'Ver Detalles', 'fr': 'Voir Détails', 'de': 'Details anzeigen', 'ar': 'عرض التفاصيل'
    },
    'Search patients': {
        'hi': 'मरीज़ खोजें', 'ta': 'நோயாளிகளைத் தேடுங்கள்', 'te': 'రోగులను వెతకండి', 'bn': 'রোগী অনুসন্ধান করুন',
        'mr': 'रुग्ण शोधा', 'gu': 'દર્દીઓ શોધો', 'kn': 'ರೋಗಿಗಳನ್ನು ಹುಡುಕಿ', 'ml': 'രോഗികളെ തിരയുക',
        'es': 'Buscar pacientes', 'fr': 'Rechercher des patients', 'de': 'Patienten suchen', 'ar': 'البحث عن المرضى'
    },
    'Name': {
        'hi': 'नाम', 'ta': 'பெயர்', 'te': 'పేరు', 'bn': 'নাম',
        'mr': 'नाव', 'gu': 'નામ', 'kn': 'ಹೆಸರು', 'ml': 'പേര്',
        'es': 'Nombre', 'fr': 'Nom', 'de': 'Name', 'ar': 'الاسم'
    },
    'Age': {
        'hi': 'उम्र', 'ta': 'வயது', 'te': 'వయస్సు', 'bn': 'বয়স',
        'mr': 'वय', 'gu': 'ઉંમર', 'kn': 'ವಯಸ್ಸು', 'ml': 'പ്രായം',
        'es': 'Edad', 'fr': 'Âge', 'de': 'Alter', 'ar': 'العمر'
    },
    'Gender': {
        'hi': 'लिंग', 'ta': 'பாலினம்', 'te': 'లింగం', 'bn': 'লিঙ্গ',
        'mr': 'लिंग', 'gu': 'જાતિ', 'kn': 'ಲಿಂಗ', 'ml': 'ലിംഗം',
        'es': 'Género', 'fr': 'Genre', 'de': 'Geschlecht', 'ar': 'الجنس'
    },
    'Male': {
        'hi': 'पुरुष', 'ta': 'ஆண்', 'te': 'పురుషుడు', 'bn': 'পুরুষ',
        'mr': 'पुरुष', 'gu': 'પુરુષ', 'kn': 'ಪುರುಷ', 'ml': 'പുരുഷൻ',
        'es': 'Masculino', 'fr': 'Masculin', 'de': 'Männlich', 'ar': 'ذكر'
    },
    'Female': {
        'hi': 'महिला', 'ta': 'பெண்', 'te': 'స్త్రీ', 'bn': 'মহিলা',
        'mr': 'स्त्री', 'gu': 'સ્ત્રી', 'kn': 'ಮಹಿಳೆ', 'ml': 'സ്ത്രീ',
        'es': 'Femenino', 'fr': 'Féminin', 'de': 'Weiblich', 'ar': 'أنثى'
    },
    'Other': {
        'hi': 'अन्य', 'ta': 'மற்றவை', 'te': 'ఇతర', 'bn': 'অন্যান্য',
        'mr': 'इतर', 'gu': 'અન્ય', 'kn': 'ಇತರೆ', 'ml': 'മറ്റുള്ളവ',
        'es': 'Otro', 'fr': 'Autre', 'de': 'Andere', 'ar': 'آخر'
    },
    'Contact': {
        'hi': 'संपर्क', 'ta': 'தொடர்பு', 'te': 'సంప్రదింపు', 'bn': 'যোগাযোগ',
        'mr': 'संपर्क', 'gu': 'સંપર્ક', 'kn': 'ಸಂಪರ್ಕ', 'ml': 'ബന്ധപ്പെടുക',
        'es': 'Contacto', 'fr': 'Contact', 'de': 'Kontakt', 'ar': 'جهة الاتصال'
    },
    'Address': {
        'hi': 'पता', 'ta': 'முகவரி', 'te': 'చిరునామా', 'bn': 'ঠিকানা',
        'mr': 'पत्ता', 'gu': 'સરનામું', 'kn': 'ವಿಳಾಸ', 'ml': 'മേൽവിലാസം',
        'es': 'Dirección', 'fr': 'Adresse', 'de': 'Adresse', 'ar': 'العنوان'
    },
    'Medical History': {
        'hi': 'चिकित्सा इतिहास', 'ta': 'மருத்துவ வரலாறு', 'te': 'వైద్య చరిత్ర', 'bn': 'চিকিৎসার ইতিহাস',
        'mr': 'वैद्यकीय इतिहास', 'gu': 'તબીબી ઇતિહાસ', 'kn': 'ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ', 'ml': 'ചികിത്സാ ചരിത്രം',
        'es': 'Historial Médico', 'fr': 'Antécédents Médicaux', 'de': 'Krankengeschichte', 'ar': 'التاريخ الطبي'
    },
    'Save Patient': {
        'hi': 'मरीज़ सहेजें', 'ta': 'நோயாளியைச் சேமிக்கவும்', 'te': 'రోగిని భద్రపరచండి', 'bn': 'রোগী সংরক্ষণ করুন',
        'mr': 'रुग्ण जतन करा', 'gu': 'દર્દી સાચવો', 'kn': 'ರೋಗಿಯನ್ನು ಉಳಿಸಿ', 'ml': 'രോഗിയെ സൂക്ഷിക്കുക',
        'es': 'Guardar Paciente', 'fr': 'Enregistrer Patient', 'de': 'Patient speichern', 'ar': 'حفظ المريض'
    },
    'Cancel': {
        'hi': 'रद्द करें', 'ta': 'ரத்துசெய்', 'te': 'రద్దు చేయండి', 'bn': 'বাতিল করুন',
        'mr': 'रद्द करा', 'gu': 'રદ કરો', 'kn': 'ರದ್ದುಮಾಡಿ', 'ml': 'റദ്ദാക്കുക',
        'es': 'Cancelar', 'fr': 'Annuler', 'de': 'Abbrechen', 'ar': 'إلغاء'
    },

    # Body Parts & Anatomy
    'Chest': {
        'hi': 'छाती', 'ta': 'மார்பு', 'te': 'ఛాతీ', 'bn': 'বুক',
        'mr': 'छाती', 'gu': 'છાતી', 'kn': 'ಎದೆ', 'ml': 'നെഞ്ച്',
        'es': 'Tórax', 'fr': 'Thorax', 'de': 'Brustkorb', 'ar': 'الصدر'
    },
    'Hand': {
        'hi': 'हाथ', 'ta': 'கை', 'te': 'చేయి', 'bn': 'হাত',
        'mr': 'हात', 'gu': 'હાથ', 'kn': 'ಕೈ', 'ml': 'കൈ',
        'es': 'Mano', 'fr': 'Main', 'de': 'Hand', 'ar': 'اليد'
    },
    'Leg': {
        'hi': 'पैर', 'ta': 'கால்', 'te': 'కాలు', 'bn': 'পা',
        'mr': 'पाय', 'gu': 'પગ', 'kn': 'ಕಾಲು', 'ml': 'കാൽ',
        'es': 'Pierna', 'fr': 'Jambe', 'de': 'Bein', 'ar': 'الساق'
    },
    'Skull': {
        'hi': 'खोपड़ी', 'ta': 'மண்டை ஓடு', 'te': 'పుర్రె', 'bn': 'মাথার খুলি',
        'mr': 'कवटी', 'gu': 'ખોપરી', 'kn': 'ತಲೆಬುರುಡೆ', 'ml': 'തലയോട്ടി',
        'es': 'Cráneo', 'fr': 'Crâne', 'de': 'Schädel', 'ar': 'الجمجمة'
    },
    'Spine': {
        'hi': 'रीढ़ की हड्डी', 'ta': 'முதுகெலும்பு', 'te': 'వెన్నెముక', 'bn': 'মেরুদণ্ড',
        'mr': 'पाठीचा कणा', 'gu': 'કરોડરજ્જુ', 'kn': 'ಬೆನ್ನುಮೂಳೆ', 'ml': 'നട്ടെല്ല്',
        'es': 'Columna Vertebral', 'fr': 'Colonne Vertébrale', 'de': 'Wirbelsäule', 'ar': 'العمود الفقري'
    },
    'Pelvis': {
        'hi': 'श्रोणि', 'ta': 'இடுப்பு எலும்பு', 'te': 'కటి భాగం', 'bn': 'শ্রোণীচক্র',
        'mr': 'श्रोणी', 'gu': 'પેલ્વિસ', 'kn': 'ಪೆಲ್ವಿಸ್', 'ml': 'ഇടുപ്പ് അസ്ഥി',
        'es': 'Pelvis', 'fr': 'Bassin', 'de': 'Becken', 'ar': 'الحوض'
    },

    # Medical Conditions & Findings
    'Normal': {
        'hi': 'सामान्य (रोगमुक्त)', 'ta': 'இயல்பானது', 'te': 'సాధారణం', 'bn': 'স্বাভাবিক',
        'mr': 'सामान्य', 'gu': 'સામાન્ય', 'kn': 'ಸಾಮಾನ್ಯ', 'ml': 'സാധാരണം',
        'es': 'Normal', 'fr': 'Normal', 'de': 'Normal', 'ar': 'طبيعي'
    },
    'Pneumonia': {
        'hi': 'निमोनिया', 'ta': 'நிமோனியா', 'te': 'న్యుమోనియా', 'bn': 'নিউমোনিয়া',
        'mr': 'न्यूमोनिया', 'gu': 'ન્યુમોનિયા', 'kn': 'ನ್ಯುಮೋನಿಯಾ', 'ml': 'ന്യുമോണിയ',
        'es': 'Neumonía', 'fr': 'Pneumonie', 'de': 'Lungenentzündung', 'ar': 'الالتهاب الرئوي'
    },
    'COVID-19': {
        'hi': 'कोविड-19', 'ta': 'கோவிட்-19', 'te': 'కోవిడ్-19', 'bn': 'কোভিড-১৯',
        'mr': 'कोविड-१९', 'gu': 'કોવિડ-૧૯', 'kn': 'ಕೋವಿಡ್-19', 'ml': 'കോവിഡ്-19',
        'es': 'COVID-19', 'fr': 'COVID-19', 'de': 'COVID-19', 'ar': 'كوفيد-19'
    },
    'Tuberculosis': {
        'hi': 'तपेदिक (टीबी)', 'ta': 'காசநோய் (டிபி)', 'te': 'క్షయవ్యాధి (టీబీ)', 'bn': 'যক্ষ্মা (টিবি)',
        'mr': 'क्षयरोग (टीबी)', 'gu': 'ક્ષયરોગ (ટીબી)', 'kn': 'ಕ್ಷಯರೋಗ (ಟಿಬಿ)', 'ml': 'ക്ഷയരോഗം (ടിബി)',
        'es': 'Tuberculosis', 'fr': 'Tuberculose', 'de': 'Tuberkulose', 'ar': 'السل'
    },
    'Lung Cancer': {
        'hi': 'फेफड़ों का कैंसर', 'ta': 'நுரையீரல் புற்றுநோய்', 'te': 'ఊపిరితిత్తుల క్యాన్సర్', 'bn': 'ফুসফুসের ক্যান্সার',
        'mr': 'फुफ्फुसाचा कर्करोग', 'gu': 'ફેફસાનું કેન્સર', 'kn': 'ಶ್ವಾಸಕೋಶದ ಕ್ಯಾನ್ಸರ್', 'ml': 'ശ്വാസകോശ അർബുദം',
        'es': 'Cáncer de Pulmón', 'fr': 'Cancer du Poumon', 'de': 'Lungenkrebs', 'ar': 'سرطان الرئة'
    },
    'Pneumothorax': {
        'hi': 'न्यूमोथोरैक्स', 'ta': 'நியூமோதோராக்ஸ்', 'te': 'న్యుమోథొరాక్స్', 'bn': 'নিউমোথোরাক্স',
        'mr': 'न्यूमोथोरॅक्स', 'gu': 'ન્યુમોથોરેક્સ', 'kn': 'ನ್ಯೂಮೋಥೊರಾಕ್ಸ್', 'ml': 'ന്യൂമോതൊറാക്സ്',
        'es': 'Neumotórax', 'fr': 'Pneumothorax', 'de': 'Pneumothorax', 'ar': 'استرواح الصدر'
    },
    'Fracture': {
        'hi': 'अस्थिभंग (फ्रैक्चर)', 'ta': 'எலும்பு முறிவு', 'te': 'ఎముక విరుపు', 'bn': 'হাড় ভাঙা (ফ্র্যাকচার)',
        'mr': 'हाड मोडणे (फ्रॅक्चर)', 'gu': 'હાડકું તૂટવું', 'kn': 'ಮೂಳೆ ಮುರಿತ', 'ml': 'അസ്ഥി ഒടിവ്',
        'es': 'Fractura Ósea', 'fr': 'Fracture', 'de': 'Knochenbruch', 'ar': 'كسر عظمي'
    },
    'Arthritis': {
        'hi': 'गठिया (आर्थराइटिस)', 'ta': 'மூட்டுவலி (ஆர்த்ரிடிஸ்)', 'te': 'కీళ్లవాతం', 'bn': 'গেঁটেবাত (বাত)',
        'mr': 'संधिवात', 'gu': 'સંધિવા', 'kn': 'ಸಂಧಿವಾತ', 'ml': 'സന്ധിവാതം',
        'es': 'Artritis', 'fr': 'Arthrite', 'de': 'Arthritis', 'ar': 'التهاب المفاصل'
    },
    'Dislocation': {
        'hi': 'जोड़ उतरना', 'ta': 'மூட்டு விலகல்', 'te': 'కీలు తొలగుట', 'bn': 'সন্ধিচ্যুতি',
        'mr': 'सांधा निखळणे', 'gu': 'સાંધો ખસી જવો', 'kn': 'ಕೀಲು ತಪ್ಪುವುದು', 'ml': 'സന്ധി സ്ഥാനഭ്രംശം',
        'es': 'Dislocación', 'fr': 'Dislocation', 'de': 'Verrenkung', 'ar': 'خلع المفصل'
    },
    'Bone Tumor': {
        'hi': 'हड्डी का ट्यूमर', 'ta': 'எலும்பு கட்டி', 'te': 'ఎముక కణితి', 'bn': 'হাড়ের টিউমার',
        'mr': 'हाडाचा ट्यूमर', 'gu': 'હાડકાની ગાંઠ', 'kn': 'ಮೂಳೆಯ ಗಡ್ಡೆ', 'ml': 'അസ്ഥി ട്യൂമർ',
        'es': 'Tumor Óseo', 'fr': 'Tumeur Osseuse', 'de': 'Knochentumor', 'ar': 'ورم عظمي'
    },
    'Tumor': {
        'hi': 'ट्यूमर', 'ta': 'கட்டி', 'te': 'కణితి', 'bn': 'টিউমার',
        'mr': 'ट्यूमर', 'gu': 'ગાંઠ', 'kn': 'ಗಡ್ಡೆ', 'ml': 'ട്യൂമർ',
        'es': 'Tumor', 'fr': 'Tumeur', 'de': 'Tumor', 'ar': 'ورم'
    },
    'Hemorrhage': {
        'hi': 'रक्तस्राव (हेमरेज)', 'ta': 'ரத்தக்கசிவு', 'te': 'రక్తస్రావం', 'bn': 'রক্তক্ষরণ',
        'mr': 'रक्तस्त्राव', 'gu': 'રક્તસ્ત્રાવ', 'kn': 'ರಕ್ತಸ್ರಾವ', 'ml': 'രക്തസ്രാവം',
        'es': 'Hemorragia', 'fr': 'Hémorragie', 'de': 'Blutung', 'ar': 'نزيف'
    },
    'Scoliosis': {
        'hi': 'स्कोलियोसिस (रीढ़ का टेढ़ापन)', 'ta': 'முதுகெலும்பு வளைவு', 'te': 'స్కోలియోసిస్', 'bn': 'মেরুদণ্ডের বক্রতা',
        'mr': 'स्कोलिओसिस', 'gu': 'સ્કોલિયોસિસ', 'kn': 'ಸ್ಕೋಲಿಯೋಸಿಸ್', 'ml': 'സ്കോളിയോസിസ്',
        'es': 'Escoliosis', 'fr': 'Scoliose', 'de': 'Skoliose', 'ar': 'الجنف'
    },
    'Disc Herniation': {
        'hi': 'डिस्क हर्नियेशन (स्लिप डिस्क)', 'ta': 'டிஸ்க் ஹெர்னியேஷன்', 'te': 'డిస్క్ హెర్నియేషన్', 'bn': 'ডিস্ক হার্নিয়েশন',
        'mr': 'डिस्क हर्निएशन', 'gu': 'ડિસ્ક હર્નિયેશન', 'kn': 'ಡಿಸ್ಕ್ ಹರ್ನಿಯೇಷನ್', 'ml': 'ഡിസ്ക് ഹെർണിയേഷൻ',
        'es': 'Hernia Discal', 'fr': 'Hernie Discale', 'de': 'Bandscheibenvorfall', 'ar': 'الانزلاق الغضروفي'
    },
    'Hip Dysplasia': {
        'hi': 'हिप डिसप्लेसिया', 'ta': 'இடுப்பு பிறழ்வு', 'te': 'హిప్ డిస్ప్లాసియా', 'bn': 'হিপ ডিসপ্লাসিয়া',
        'mr': 'हिप डिप्लेजिया', 'gu': 'હિપ ડિસ્પ્લેસિયા', 'kn': 'ಹಿಪ್ ಡಿಸ್ಪ್ಲಾಸಿಯಾ', 'ml': 'ഹിപ് ഡിസ്പ്ലാസിയ',
        'es': 'Displasia de Cadera', 'fr': 'Dysplasie de la Hanche', 'de': 'Hüftdysplasie', 'ar': 'خلل التنسج الوركي'
    },

    # Prediction & Report Details
    'Medical Diagnosis Report': {
        'hi': 'चिकित्सा निदान रिपोर्ट', 'ta': 'மருத்துவ நோயறிதல் அறிக்கை', 'te': 'వైద్య నిర్ధారణ నివేదిక', 'bn': 'চিকিৎসা নির্ণয় প্রতিবেদন',
        'mr': 'वैद्यकीय निदान अहवाल', 'gu': 'તબીબી નિદાન અહેવાલ', 'kn': 'ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯ ವರದಿ', 'ml': 'മെഡിക്കൽ ഡയഗ്നോസിസ് റിപ്പോർട്ട്',
        'es': 'Informe de Diagnóstico Médico', 'fr': 'Rapport de Diagnostic Médical', 'de': 'Medizinischer Diagnosebericht', 'ar': 'تقرير التشخيص الطبي'
    },
    'Prediction Result': {
        'hi': 'निदान परिणाम', 'ta': 'கணிப்பு முடிவு', 'te': 'అంచనా ఫలితం', 'bn': 'পূর্বাভাস ফলাফল',
        'mr': 'निदान निकाल', 'gu': 'અંદાજ પરિણામ', 'kn': 'ಮುನ್ಸೂಚನೆ ಫಲಿತಾಂಶ', 'ml': 'രോഗനിർണ്ണയ ഫലം',
        'es': 'Resultado del Diagnóstico', 'fr': 'Résultat du Diagnostic', 'de': 'Diagnoseergebnis', 'ar': 'نتيجة التشخيص'
    },
    'Confidence Score': {
        'hi': 'सटीकता स्कोर', 'ta': 'நம்பகத்தன்மை மதிப்பீடு', 'te': 'విశ్వసనీయత స్కోరు', 'bn': 'নির্ভুলতার মাত্রা',
        'mr': 'अचूकता गुणांक', 'gu': 'વિશ્વાસ સ્કોર', 'kn': 'ವಿಶ್ವಾಸಾರ್ಹತೆ ಸ್ಕೋರ್', 'ml': 'വിശ്വാസ്യത സ്കോർ',
        'es': 'Nivel de Confianza', 'fr': 'Score de Confiance', 'de': 'Konfidenzwert', 'ar': 'درجة الثقة'
    },
    'Body Part': {
        'hi': 'शरीर का अंग', 'ta': 'உடல் உறுப்பு', 'te': 'శరీర భాగం', 'bn': 'শরীরের অঙ্গ',
        'mr': 'शरीराचा अवयव', 'gu': 'શરીરનો ભાગ', 'kn': 'ದೇಹದ ಭಾಗ', 'ml': 'ശരീര ഭാഗം',
        'es': 'Región Anatómica', 'fr': 'Région Anatomique', 'de': 'Körperregion', 'ar': 'العضو / المنطقة'
    },
    'Scan Date': {
        'hi': 'स्कैन तिथि', 'ta': 'ஸ்கேன் தேதி', 'te': 'స్కాన్ తేదీ', 'bn': 'স্ক্যান তারিখ',
        'mr': 'स्कॅन तारीख', 'gu': 'સ્કેન તારીખ', 'kn': 'ಸ್ಕ್ಯಾನ್ ದಿನಾಂಕ', 'ml': 'സ്കാൻ തീയതി',
        'es': 'Fecha del Escaneo', 'fr': 'Date de l\'Analyse', 'de': 'Scandatum', 'ar': 'تاريخ الفحص'
    },
    'Interactive Grad-CAM Heatmap': {
        'hi': 'इंटरैक्टिव ग्रैड-सीएएम हीटमैप', 'ta': 'ஊடாடும் கிராட்-கேம் வெப்ப வரைபடம்', 'te': 'ఇంటరాక్టివ్ గ్రాడ్-కామ్ హీట్‌మ్యాప్', 'bn': 'ইন্টারেক্টিভ গ্র্যাড-ক্যাম হিটম্যাপ',
        'mr': 'इंटरअॅक्टिव्ह ग्रॅड-कॅम हीटमॅप', 'gu': 'ઇન્ટરેક્ટિવ ગ્રેડ-કેમ હીટમેપ', 'kn': 'ಇಂಟರಾಕ್ಟಿವ್ ಗ್ರಾಡ್-ಕ್ಯಾಮ್ ಹೀಟ್‌ಮ್ಯಾಪ್', 'ml': 'ഇന്ററാക്ടീവ് ഗ്രാഡ്-ക്യാം ഹീറ്റ്മാപ്പ്',
        'es': 'Mapa Térmico Interactivo Grad-CAM', 'fr': 'Carte Thermique Grad-CAM Interactive', 'de': 'Interaktive Grad-CAM Heatmap', 'ar': 'خريطة حرارية تفاعلية Grad-CAM'
    },
    'Heatmap Opacity': {
        'hi': 'हीटमैप पारदर्शिता', 'ta': 'வெப்ப வரைபட ஒளிபுகாமை', 'te': 'హీట్‌మ్యాప్ అపారదర్శకత', 'bn': 'হিটম্যাপ অস্বচ্ছতা',
        'mr': 'हीटमॅप अपारदर्शकता', 'gu': 'હીટમેપ અપારદર્શકતા', 'kn': 'ಹೀಟ್‌ಮ್ಯಾಪ್ ಅಪಾರದರ್ಶಕತೆ', 'ml': 'ഹീറ്റ്മാപ്പ് സുതാര്യത',
        'es': 'Opacidad del Mapa', 'fr': 'Opacité de la Carte', 'de': 'Heatmap-Deckkraft', 'ar': 'شفافية الخريطة'
    },
    'Invert Colors': {
        'hi': 'रंग उलटें', 'ta': 'நிறங்களை மாற்றுக', 'te': 'రంగులను విలోమం చేయండి', 'bn': 'রং উল্টান',
        'mr': 'रंग उलटा', 'gu': 'રંગો ઉલટાવો', 'kn': 'ಬಣ್ಣಗಳನ್ನು ತಿರುಗಿಸಿ', 'ml': 'നിറങ്ങൾ വിപരീതമാക്കുക',
        'es': 'Invertir Colores', 'fr': 'Inverser Couleurs', 'de': 'Farben invertieren', 'ar': 'عكس الألوان'
    },
    'Reset View': {
        'hi': 'दृश्य रीसेट करें', 'ta': 'பார்வையை மீட்டமைக்க', 'te': 'దృశ్యాన్ని రీసెట్ చేయండి', 'bn': 'রিসেট করুন',
        'mr': 'दृश्य रीसेट करा', 'gu': 'દૃશ્ય રીસેટ કરો', 'kn': 'ದೃಶ್ಯವನ್ನು ಮರುಹೊಂದಿಸಿ', 'ml': 'കാഴ്ച പുനഃസ്ഥാപിക്കുക',
        'es': 'Restablecer Vista', 'fr': 'Réinitialiser Vue', 'de': 'Ansicht zurücksetzen', 'ar': 'إعادة ضبط العرض'
    },
    'Differential Diagnosis & Severity': {
        'hi': 'विभेदक निदान और गंभीरता रैंकिंग', 'ta': 'வேறுபட்ட நோயறிதல் மற்றும் தீவிரம்', 'te': 'విభేదక నిర్ధారణ మరియు తీవ్రత', 'bn': 'ডিফারেনশিয়াল নির্ণয় ও তীব্রতা',
        'mr': 'तुलनात्मक निदान आणि तीव्रता', 'gu': 'તુલનાત્મક નિદાન અને ગંભીરતા', 'kn': 'ವಿಭಿನ್ನ ರೋಗನಿರ್ಣಯ ಮತ್ತು ತೀವ್ರತೆ', 'ml': 'വ്യത്യസ്ത രോഗനിർണ്ണയവും തീവ്രതയും',
        'es': 'Diagnóstico Diferencial y Severidad', 'fr': 'Diagnostic Différentiel et Gravité', 'de': 'Differenzialdiagnose & Schweregrad', 'ar': 'التشخيص التفريقي ودرجة الخطورة'
    },
    'Clinical Scribe & Physician Notes': {
        'hi': 'क्लिनिकल स्क्राइब और चिकित्सक नोट्स', 'ta': 'மருத்துவ எழுத்தர் மற்றும் மருத்துவர் குறிப்புகள்', 'te': 'క్లినికల్ స్క్రైబ్ మరియు వైద్యుల గమనికలు', 'bn': 'ক্লিনিকাল স্ক্রাইব ও চিকিৎসকের নোট',
        'mr': 'क्लिनिकल स्क्राइब आणि डॉक्टरांच्या नोंदी', 'gu': 'ક્લિનિકલ સ્ક્રાઇબ અને ડૉક્ટર નોંધો', 'kn': 'ಕ್ಲಿನಿಕಲ್ ಸ್ಕ್ರೈಬ್ ಮತ್ತು ವೈದ್ಯರ ಟಿಪ್ಪಣಿಗಳು', 'ml': 'ക്ലിനിക്കൽ സ്ക്രൈബും ഡോക്ടറുടെ കുറിപ്പുകളും',
        'es': 'Escriba Clínico y Notas del Médico', 'fr': 'Scribe Clinique et Notes du Médecin', 'de': 'Klinischer Assistent & Arztnotizen', 'ar': 'الكاتب السريري وملاحظات الطبيب'
    },
    'Dictate Notes': {
        'hi': 'बोलकर लिखें (डिक्टेट)', 'ta': 'பேசி எழுதுக', 'te': 'వాయిస్ ద్వారా రాయండి', 'bn': 'মুখে বলে লিখুন',
        'mr': 'बोलून नोंदवा', 'gu': 'બોલીને લખો', 'kn': 'ಧ್ವನಿ ಮೂಲಕ ಬರೆಯಿರಿ', 'ml': 'ശബ്ദം വഴി രേഖപ്പെടുത്തുക',
        'es': 'Dictar Notas', 'fr': 'Dicter des Notes', 'de': 'Notizen diktieren', 'ar': 'إملاء صوتي'
    },
    'Save Notes': {
        'hi': 'नोट्स सहेजें', 'ta': 'குறிப்புகளைச் சேமிக்கவும்', 'te': 'గమనికలను భద్రపరచండి', 'bn': 'নোট সংরক্ষণ করুন',
        'mr': 'नोंदी जतन करा', 'gu': 'નોંધો સાચવો', 'kn': 'ಟಿಪ್ಪಣಿಗಳನ್ನು ಉಳಿಸಿ', 'ml': 'കുറിപ്പുകൾ സേവ് ചെയ്യുക',
        'es': 'Guardar Notas', 'fr': 'Enregistrer Notes', 'de': 'Notizen speichern', 'ar': 'حفظ الملاحظات'
    },
    'Medical Recommendations': {
        'hi': 'चिकित्सा परामर्श और दिशानिर्देश', 'ta': 'மருத்துவ பரிந்துரைகள்', 'te': 'వైద్య సిఫార్సులు', 'bn': 'চিকিৎসা সংক্রান্ত পরামর্শ',
        'mr': 'वैद्यकीय शिफारसी', 'gu': 'તબીબી ભલામણો', 'kn': 'ವೈದ್ಯಕೀಯ ಶಿಫಾರಸುಗಳು', 'ml': 'ചികിത്സാ നിർദ്ദേശങ്ങൾ',
        'es': 'Recomendaciones Médicas', 'fr': 'Recommandations Médicales', 'de': 'Medizinische Empfehlungen', 'ar': 'التوصيات الطبية'
    },
    'Dietary Recommendations': {
        'hi': 'आहार संबंधी सुझाव', 'ta': 'உணவுமுறை பரிந்துரைகள்', 'te': 'ఆహార సిఫార్సులు', 'bn': 'খাদ্যতালিকা সংক্রান্ত পরামর্শ',
        'mr': 'आहार विषयक सल्ला', 'gu': 'આહાર ભલામણો', 'kn': 'ಆಹಾರ ಶಿಫಾರಸುಗಳು', 'ml': 'ഭക്ഷണ ക്രമീകരണ നിർദ്ദേശങ്ങൾ',
        'es': 'Recomendaciones Dietéticas', 'fr': 'Recommandations Diététiques', 'de': 'Ernährungsempfehlungen', 'ar': 'إرشادات الحمية الغذائية'
    },
    'Exercise Guidelines': {
        'hi': 'व्यायाम दिशानिर्देश', 'ta': 'உடற்பயிற்சி வழிகாட்டுதல்கள்', 'te': 'వ్యాయామ మార్గదర్శకాలు', 'bn': 'ব্যায়াম নির্দেশিকা',
        'mr': 'व्यायाम मार्गदर्शक तत्त्वे', 'gu': 'કસરત માર્ગદર્શિકા', 'kn': 'ವ್ಯಾಯಾಮ ಮಾರ್ಗಸೂಚಿಗಳು', 'ml': 'വ്യായാമ നിർദ്ദേശങ്ങൾ',
        'es': 'Guía de Ejercicios', 'fr': 'Conseils d\'Exercice', 'de': 'Übungsrichtlinien', 'ar': 'إرشادات التمارين الرياضية'
    },
    'Download Official PDF Report': {
        'hi': 'आधिकारिक पीडीएफ रिपोर्ट डाउनलोड करें', 'ta': 'அதிகாரப்பூர்வ PDF அறிக்கையைப் பதிவிறக்குக', 'te': 'అధికారిక PDF నివేదికను డౌన్‌లోడ్ చేయండి', 'bn': 'অফিসিয়াল PDF রিপোর্ট ডাউনলোড করুন',
        'mr': 'अधिकृत पीडीएफ अहवाल डाउनलोड करा', 'gu': 'સત્તાવાર PDF રિપોર્ટ ડાઉનલોડ કરો', 'kn': 'ಅಧಿಕೃತ PDF ವರದಿಯನ್ನು ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ', 'ml': 'ഔദ്യോഗിക PDF റിപ്പോർട്ട് ഡൗൺലോഡ് ചെയ്യുക',
        'es': 'Descargar Informe Oficial en PDF', 'fr': 'Télécharger Rapport PDF Officiel', 'de': 'Offiziellen PDF-Bericht herunterladen', 'ar': 'تحميل التقرير الطبي الرسمي PDF'
    },
    'Print Report': {
        'hi': 'रिपोर्ट प्रिंट करें', 'ta': 'அறிக்கையை அச்சிடுக', 'te': 'నివేదికను ప్రింట్ చేయండి', 'bn': 'রিপোর্ট প্রিন্ট করুন',
        'mr': 'अहवाल मुद्रित करा', 'gu': 'રિપોર્ટ પ્રિન્ટ કરો', 'kn': 'ವರದಿಯನ್ನು ಮುದ್ರಿಸಿ', 'ml': 'റിപ്പോർട്ട് പ്രിന്റ് ചെയ്യുക',
        'es': 'Imprimir Informe', 'fr': 'Imprimer le Rapport', 'de': 'Bericht drucken', 'ar': 'طباعة التقرير'
    },
    'Compare with Previous Scans': {
        'hi': 'पिछले स्कैन से तुलना करें', 'ta': 'முந்தைய ஸ்கேன்களுடன் ஒப்பிடவும்', 'te': 'మునుపటి స్కాన్‌లతో పోల్చండి', 'bn': 'আগের স্ক্যানের সাথে তুলনা করুন',
        'mr': 'मागील स्कॅनशी तुलना करा', 'gu': 'પાછલા સ્કેન સાથે સરખામણી કરો', 'kn': 'ಹಿಂದಿನ ಸ್ಕ್ಯಾನ್‌ಗಳೊಂದಿಗೆ ಹೋಲಿಸಿ', 'ml': 'മുൻകാല സ്കാനുകളുമായി താരതമ്യം ചെയ്യുക',
        'es': 'Comparar con Escaneos Anteriores', 'fr': 'Comparer avec les Analyses Précédentes', 'de': 'Mit früheren Scans vergleichen', 'ar': 'مقارنة مع الفحوصات السابقة'
    },
    'Longitudinal Scan Comparison': {
        'hi': 'अनुदैर्ध्य स्कैन तुलना (समय अनुसार)', 'ta': 'நீளமான ஸ்கேன் ஒப்பீடு', 'te': 'కాలక్రమానుసార స్కాన్ పోలిక', 'bn': 'সময়ভিত্তিক স্ক্যান তুলনা',
        'mr': 'कालक्रमानुसार स्कॅन तुलना', 'gu': 'સમય અનુસાર સ્કેન સરખામણી', 'kn': 'ಕಾಲಾನುಕ್ರಮಣಿಕ ಸ್ಕ್ಯಾನ್ ಹೋಲಿಕೆ', 'ml': 'കാലാനുസൃതമായ സ്കാൻ താരതമ്യം',
        'es': 'Comparación Longitudinal de Escaneos', 'fr': 'Comparaison d\'Analyses Longitudinales', 'de': 'Longitudinale Scan-Vergleichsanalyse', 'ar': 'المقارنة التتبعية للفحوصات'
    },
    'Baseline Scan': {
        'hi': 'प्रारंभिक स्कैन (बेसलाइन)', 'ta': 'அடிப்படை ஸ்கேன்', 'te': 'ప్రారంభ స్కాన్', 'bn': 'প্রাথমিক স্ক্যান',
        'mr': 'मूळ स्कॅन', 'gu': 'પ્રારંભિક સ્કેન', 'kn': 'ಆರಂಭಿಕ ಸ್ಕ್ಯಾನ್', 'ml': 'പ്രാരംഭ സ്കാൻ',
        'es': 'Escaneo Inicial', 'fr': 'Analyse Initiale', 'de': 'Basis-Scan', 'ar': 'الفحص الأولي'
    },
    'Follow-up Scan': {
        'hi': 'अनुवर्ती स्कैन (फॉलो-अप)', 'ta': 'தொடர் கண்காணிப்பு ஸ்கேன்', 'te': 'తదుపరి స్కాన్', 'bn': 'পরবর্তী ফলো-আপ স্ক্যান',
        'mr': 'फॉलो-अप स्कॅन', 'gu': 'ફોલો-અપ સ્કેન', 'kn': 'ಫಾಲೋ-ಅಪ್ ಸ್ಕ್ಯಾನ್', 'ml': 'തുടർ സ്കാൻ',
        'es': 'Escaneo de Seguimiento', 'fr': 'Analyse de Suivi', 'de': 'Nachuntersuchungsscan', 'ar': 'فحص المتابعة'
    },
    'Upload Medical X-Ray': {
        'hi': 'मेडिकल एक्स-रे अपलोड करें', 'ta': 'மருத்துவ எக்ஸ்-ரே பதிவேற்றவும்', 'te': 'వైద్య ఎక్స్-రే అప్‌లోడ్ చేయండి', 'bn': 'মেডিকেল এক্স-রে আপলোড করুন',
        'mr': 'वैद्यकीय क्ष-किरण अपलोड करा', 'gu': 'તબીબી એક્સ-રે અપલોડ કરો', 'kn': 'ವೈದ್ಯಕೀಯ ಕ್ಷ-ಕಿರಣ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ', 'ml': 'മെഡിക്കൽ എക്സ്-റേ അപ്‌ലോഡ് ചെയ്യുക',
        'es': 'Subir Radiografía Médica', 'fr': 'Télécharger Radiographie Médicale', 'de': 'Röntgenaufnahme hochladen', 'ar': 'تحميل الأشعة السينية الطبية'
    },
    'Select Patient': {
        'hi': 'मरीज़ चुनें', 'ta': 'நோயாளியைத் தேர்ந்தெடுக்கவும்', 'te': 'రోగిని ఎంచుకోండి', 'bn': 'রোগী নির্বাচন করুন',
        'mr': 'रुग्ण निवडा', 'gu': 'દર્દી પસંદ કરો', 'kn': 'ರೋಗಿಯನ್ನು ಆಯ್ಕೆಮಾಡಿ', 'ml': 'രോഗിയെ തിരഞ്ഞെടുക്കുക',
        'es': 'Seleccionar Paciente', 'fr': 'Sélectionner Patient', 'de': 'Patient auswählen', 'ar': 'اختيار المريض'
    },
    'Select Body Part': {
        'hi': 'शरीर का अंग चुनें', 'ta': 'உறுப்பைத் தேர்ந்தெடுக்கவும்', 'te': 'శరీర భాగాన్ని ఎంచుకోండి', 'bn': 'অঙ্গ নির্বাচন করুন',
        'mr': 'शरीराचा अवयव निवडा', 'gu': 'શરીરનો ભાગ પસંદ કરો', 'kn': 'ದೇಹದ ಭಾಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ', 'ml': 'ശരീര ഭാഗം തിരഞ്ഞെടുക്കുക',
        'es': 'Seleccionar Región Anatómica', 'fr': 'Sélectionner Région', 'de': 'Körperregion auswählen', 'ar': 'اختيار الجزء المصاب'
    },
    'Analyze X-Ray': {
        'hi': 'एक्स-रे का विश्लेषण करें', 'ta': 'எக்ஸ்-ரேவை ஆய்வு செய்க', 'te': 'ఎక్స్-రేను విశ్లేషించండి', 'bn': 'এক্স-রে বিশ্লেষণ করুন',
        'mr': 'क्ष-किरणाचे विश्लेषण करा', 'gu': 'એક્સ-રેનું વિશ્લેષણ કરો', 'kn': 'ಕ್ಷ-ಕಿರಣವನ್ನು ವಿಶ್ಲೇಷಿಸಿ', 'ml': 'എക്സ്-റേ വിശകലനം ചെയ്യുക',
        'es': 'Analizar Radiografía', 'fr': 'Analyser Radiographie', 'de': 'Röntgenbild analysieren', 'ar': 'تحليل الأشعة السينية'
    },
    'Drag and drop X-ray image here, or click to browse': {
        'hi': 'एक्स-रे छवि यहां खींचें और छोड़ें, या चुनने के लिए क्लिक करें',
        'ta': 'எக்ஸ்-ரே படத்தை இங்கே இழுத்துப் போடவும் அல்லது தேர்ந்தெடுக்க கிளிக் செய்யவும்',
        'te': 'ఎక్స్-రే చిత్రాన్ని ఇక్కడ లాగండి లేదా బ్రౌజ్ చేయడానికి క్లిక్ చేయండి',
        'bn': 'এখানে এক্স-রে ছবি টেনে আনুন অথবা নির্বাচন করতে ক্লিক করুন',
        'mr': 'क्ष-किरण प्रतिमा येथे ड्रॅग आणि ड्रॉप करा, किंवा ब्राउझ करण्यासाठी क्लिक करा',
        'gu': 'એક્સ-રે છબી અહીં મૂકો અથવા પસંદ કરવા ક્લિક કરો',
        'kn': 'ಕ್ಷ-ಕಿರಣ ಚಿತ್ರವನ್ನು ಇಲ್ಲಿಗೆ ಎಳೆಯಿರಿ ಅಥವಾ ಆಯ್ಕೆ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ',
        'ml': 'എക്സ്-റേ ചിത്രം ഇവിടെ ഇടുക അല്ലെങ്കിൽ തിരഞ്ഞെടുക്കാൻ ക്ലിക്ക് ചെയ്യുക',
        'es': 'Arrastre la imagen de rayos X aquí o haga clic para buscar',
        'fr': 'Glissez et déposez l\'image radiographique ici ou cliquez pour parcourir',
        'de': 'Röntgenbild hierher ziehen oder zum Durchsuchen klicken',
        'ar': 'اسحب وأفلت صورة الأشعة السينية هنا أو اضغط للاستعراض'
    },
    'Supports DICOM (.dcm), JPEG, PNG': {
        'hi': 'DICOM (.dcm), JPEG, PNG समर्थित है',
        'ta': 'DICOM (.dcm), JPEG, PNG ஆதரிக்கப்படுகிறது',
        'te': 'DICOM (.dcm), JPEG, PNG ఫార్మాట్‌లకు మద్దతు ఉంది',
        'bn': 'DICOM (.dcm), JPEG, PNG সমর্থন করে',
        'mr': 'DICOM (.dcm), JPEG, PNG समर्थित',
        'gu': 'DICOM (.dcm), JPEG, PNG સપોર્ટેડ',
        'kn': 'DICOM (.dcm), JPEG, PNG ಬೆಂಬಲಿತವಾಗಿದೆ',
        'ml': 'DICOM (.dcm), JPEG, PNG പിന്തുണയ്ക്കുന്നു',
        'es': 'Soporta DICOM (.dcm), JPEG, PNG',
        'fr': 'Prend en charge DICOM (.dcm), JPEG, PNG',
        'de': 'Unterstützt DICOM (.dcm), JPEG, PNG',
        'ar': 'يدعم DICOM (.dcm) و JPEG و PNG'
    },
    'AI for Smarter Disease Detection': {
        'hi': 'स्मार्ट रोग निदान के लिए कृत्रिम बुद्धिमत्ता (AI)',
        'ta': 'புத்திசாலித்தனமான நோய் கண்டறிதலுக்கான AI',
        'te': 'స్మార్ట్ వ్యాధి నిర్ధారణ కోసం AI',
        'bn': 'স্মার্ট রোগ নির্ণয়ের জন্য কৃত্রিম বুদ্ধিমত্তা',
        'mr': 'स्मार्ट रोग निदानासाठी कृत्रिम बुद्धिमत्ता',
        'gu': 'સ્માર્ટ રોગ નિદાન માટે AI',
        'kn': 'ಸ್ಮಾರ್ಟ್ ರೋಗ ಪತ್ತೆಗಾಗಿ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ',
        'ml': 'സ്മാർട്ട് രോഗനിർണയത്തിനായുള്ള ആർട്ടിഫിഷ്യൽ ഇന്റലിജൻസ്',
        'es': 'IA para Detección Inteligente de Enfermedades',
        'fr': 'L\'IA pour une Détection Plus Intelligente des Maladies',
        'de': 'KI für intelligentere Krankheitserkennung',
        'ar': 'الذكاء الاصطناعي لتشخيص أدق للأمراض'
    },
    'Empowering healthcare with artificial intelligence': {
        'hi': 'कृत्रिम बुद्धिमत्ता के साथ स्वास्थ्य सेवा को सशक्त बनाना',
        'ta': 'செயற்கை நுண்ணறிவால் சுகாதார சேவையை மேம்படுத்துதல்',
        'te': 'కృత్రిమ మేధస్సుతో ఆరోగ్య సంరక్షణను శక్తివంతం చేయడం',
        'bn': 'কৃত্রিম বুদ্ধিমত্তার মাধ্যমে স্বাস্থ্যসেবা শক্তিশালীকরণ',
        'mr': 'कृत्रिम बुद्धिमत्तेसह आरोग्यसेवा सक्षम करणे',
        'gu': 'કૃત્રિમ બુદ્ધિમત્તા સાથે આરોગ્યસંભાળને સશક્ત બનાવવી',
        'kn': 'ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆಯೊಂದಿಗೆ ಆರೋಗ್ಯ ರಕ್ಷಣೆಯನ್ನು ಸಶಕ್ತಗೊಳಿಸುವುದು',
        'ml': 'ആർട്ടിഫിഷ്യൽ ഇന്റലിജൻസ് വഴി ആരോഗ്യസംരക്ഷണം ശാക്തീകരിക്കുന്നു',
        'es': 'Potenciando la atención médica con inteligencia artificial',
        'fr': 'Autonomiser les soins de santé grâce à l\'intelligence artificielle',
        'de': 'Gesundheitsversorgung durch künstliche Intelligenz stärken',
        'ar': 'تمكين الرعاية الصحية بالذكاء الاصطناعي'
    },
    'Welcome Back': {
        'hi': 'वापसी पर स्वागत है', 'ta': 'மீண்டும் வருக', 'te': 'తిరిగి స్వాగతం', 'bn': 'স্বাগতম',
        'mr': 'पुन्हा स्वागत आहे', 'gu': 'પાછા સ્વાગત છે', 'kn': 'ಮರಳಿ ಸ್ವಾಗತ', 'ml': 'തിരികെ സ്വാഗതം',
        'es': 'Bienvenido de Nuevo', 'fr': 'Bon retour', 'de': 'Willkommen zurück', 'ar': 'مرحبًا بعودتك'
    },
    'Sign in to your MediScan AI account': {
        'hi': 'अपने MediScan AI खाते में साइन इन करें', 'ta': 'உங்கள் MediScan AI கணக்கில் உள்நுழைக', 'te': 'మీ MediScan AI ఖాతాలోకి సైన్ ఇన్ చేయండి', 'bn': 'আপনার MediScan AI অ্যাকাউন্টে সাইন ইন করুন',
        'mr': 'तुमच्या MediScan AI खात्यात साइन इन करा', 'gu': 'તમારા MediScan AI ખાતામાં સાઇન ઇન કરો', 'kn': 'ನಿಮ್ಮ MediScan AI ಖಾತೆಗೆ ಸೈನ್ ಇನ್ ಮಾಡಿ', 'ml': 'നിങ്ങളുടെ MediScan AI അക്കൗണ്ടിലേക്ക് സൈൻ ഇൻ ചെയ്യുക',
        'es': 'Inicie sesión en su cuenta de MediScan AI', 'fr': 'Connectez-vous à votre compte MediScan AI', 'de': 'Melden Sie sich bei Ihrem MediScan AI-Konto an', 'ar': 'سجل الدخول إلى حساب MediScan AI الخاص بك'
    },
    'Create Account': {
        'hi': 'खाता बनाएं', 'ta': 'கணக்கை உருவாக்கு', 'te': 'ఖాతాను సృష్టించండి', 'bn': 'অ্যাকাউন্ট তৈরি করুন',
        'mr': 'खाते तयार करा', 'gu': 'ખાતું બનાવો', 'kn': 'ಖಾತೆ ರಚಿಸಿ', 'ml': 'അക്കൗണ്ട് സൃഷ്ടിക്കുക',
        'es': 'Crear Cuenta', 'fr': 'Créer un Compte', 'de': 'Konto erstellen', 'ar': 'إنشاء حساب'
    },
    'Email Address': {
        'hi': 'ईमेल पता', 'ta': 'மின்னஞ்சல் முகவரி', 'te': 'ఈమెయిల్ చిరునామా', 'bn': 'ইমেল ঠিকানা',
        'mr': 'ईमेल पत्ता', 'gu': 'ઈમેલ સરનામું', 'kn': 'ಇಮೇಲ್ ವಿಳಾಸ', 'ml': 'ഇമെയിൽ വിലാസം',
        'es': 'Dirección de Correo', 'fr': 'Adresse Email', 'de': 'E-Mail-Adresse', 'ar': 'عنوان البريد الإلكتروني'
    },
    'Password': {
        'hi': 'पासवर्ड', 'ta': 'கடவுச்சொல்', 'te': 'పాస్‌వర్డ్', 'bn': 'পাসওয়ার্ড',
        'mr': 'पासवर्ड', 'gu': 'પાસવર્ડ', 'kn': 'ಪಾಸ್‌ವರ್ಡ್', 'ml': 'പാസ്‌വേഡ്',
        'es': 'Contraseña', 'fr': 'Mot de passe', 'de': 'Passwort', 'ar': 'كلمة المرور'
    },
    'Confirm Password': {
        'hi': 'पासवर्ड की पुष्टि करें', 'ta': 'கடவுச்சொல்லை உறுதிப்படுத்தவும்', 'te': 'పాస్‌వర్డ్‌ను నిర్ధారించండి', 'bn': 'পাসওয়ার্ড নিশ্চিত করুন',
        'mr': 'पासवर्डची पुष्टी करा', 'gu': 'પાસવર્ડની પુષ્ટિ કરો', 'kn': 'ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ', 'ml': 'പാസ്‌വേഡ് സ്ഥിരീകരിക്കുക',
        'es': 'Confirmar Contraseña', 'fr': 'Confirmer le mot de passe', 'de': 'Passwort bestätigen', 'ar': 'تأكيد كلمة المرور'
    },
    'Sign In': {
        'hi': 'साइन इन करें', 'ta': 'உள்நுழைக', 'te': 'సైన్ ఇన్', 'bn': 'সাইন ইন',
        'mr': 'साइन इन करा', 'gu': 'સાઇન ઇન', 'kn': 'ಸೈನ್ ಇನ್', 'ml': 'സൈൻ ഇൻ ചെയ്യുക',
        'es': 'Iniciar Sesión', 'fr': 'Connexion', 'de': 'Anmelden', 'ar': 'تسجيل الدخول'
    },
    "Don't have an account?": {
        'hi': 'खाता नहीं है?', 'ta': 'கணக்கு இல்லையா?', 'te': 'ఖాతా లేదా?', 'bn': 'অ্যাকাউন্ট নেই?',
        'mr': 'खाते नाही का?', 'gu': 'ખાતું નથી?', 'kn': 'ಖಾತೆ ಇಲ್ಲವೇ?', 'ml': 'അക്കൗണ്ട് ഇല്ലേ?',
        'es': '¿No tiene una cuenta?', 'fr': 'Vous n\'avez pas de compte ?', 'de': 'Haben Sie noch kein Konto?', 'ar': 'ليس لديك حساب؟'
    },
    'Sign up here': {
        'hi': 'यहाँ साइन अप करें', 'ta': 'இங்கே பதிவுசெய்க', 'te': 'ఇక్కడ సైన్ అప్ చేయండి', 'bn': 'এখানে সাইন আপ করুন',
        'mr': 'येथे नोंदणी करा', 'gu': 'અહીં સાઇન અપ કરો', 'kn': 'ಇಲ್ಲಿ ಸೈನ್ ಅಪ್ ಮಾಡಿ', 'ml': 'ഇവിടെ സൈൻ അപ്പ് ചെയ്യുക',
        'es': 'Regístrese aquí', 'fr': 'Inscrivez-vous ici', 'de': 'Hier registrieren', 'ar': 'سجل هنا'
    },
    'Already have an account?': {
        'hi': 'पहले से खाता है?', 'ta': 'ஏற்கனவே கணக்கு உள்ளதா?', 'te': 'ఇప్పటికే ఖాతా ఉందా?', 'bn': 'ইতিমধ্যে একটি অ্যাকাউন্ট আছে?',
        'mr': 'आधीच खाते आहे का?', 'gu': 'પહેલેથી ખાતું છે?', 'kn': 'ಈಗಾಗಲೇ ಖಾತೆ ಹೊಂದಿದ್ದೀರಾ?', 'ml': 'ഇതിനകം അക്കൗണ്ട് ഉണ്ടോ?',
        'es': '¿Ya tiene una cuenta?', 'fr': 'Vous avez déjà un compte ?', 'de': 'Haben Sie bereits ein Konto?', 'ar': 'هل لديك حساب بالفعل؟'
    },
    'Sign in here': {
        'hi': 'यहाँ साइन इन करें', 'ta': 'இங்கே உள்நுழைக', 'te': 'ఇక్కడ సైన్ ఇన్ చేయండి', 'bn': 'এখানে সাইন ইন করুন',
        'mr': 'येथे साइन इन करा', 'gu': 'અહીં સાઇન ઇન કરો', 'kn': 'ಇಲ್ಲಿ ಸೈನ್ ಇನ್ ಮಾಡಿ', 'ml': 'ഇവിടെ സൈൻ ഇൻ ചെയ്യുക',
        'es': 'Inicie sesión aquí', 'fr': 'Connectez-vous ici', 'de': 'Hier anmelden', 'ar': 'سجل الدخول هنا'
    },
    'Patient ID': {
        'hi': 'मरीज़ आईडी', 'ta': 'நோயாளி ஐடி', 'te': 'రోగి ఐడీ', 'bn': 'রোগী আইডি',
        'mr': 'रुग्ण आयडी', 'gu': 'દર્દી આઈડી', 'kn': 'ರೋಗಿ ಐಡಿ', 'ml': 'രോഗി ഐഡി',
        'es': 'ID de Paciente', 'fr': 'ID Patient', 'de': 'Patienten-ID', 'ar': 'معرّف المريض'
    },
    'Age': {
        'hi': 'आयु', 'ta': 'வயது', 'te': 'వయస్సు', 'bn': 'বয়স',
        'mr': 'वय', 'gu': 'ઉંમર', 'kn': 'ವಯಸ್ಸು', 'ml': 'പ്രായം',
        'es': 'Edad', 'fr': 'Âge', 'de': 'Alter', 'ar': 'العمر'
    },
    'Gender': {
        'hi': 'लिंग', 'ta': 'பாலினம்', 'te': 'లింగం', 'bn': 'লিঙ্গ',
        'mr': 'लिंग', 'gu': 'જાતિ', 'kn': 'ಲಿಂಗ', 'ml': 'ലിംഗം',
        'es': 'Género', 'fr': 'Genre', 'de': 'Geschlecht', 'ar': 'الجنس'
    },
    'Blood Group': {
        'hi': 'रक्त समूह', 'ta': 'இரத்த வகை', 'te': 'రక్త గ్రూపు', 'bn': 'রক্তের গ্রুপ',
        'mr': 'रक्तगट', 'gu': 'રક્ત જૂથ', 'kn': 'ರಕ್ತದ ಗುಂಪು', 'ml': 'രക്തഗ്രൂപ്പ്',
        'es': 'Grupo Sanguíneo', 'fr': 'Groupe Sanguin', 'de': 'Blutgruppe', 'ar': 'فصيلة الدم'
    },
    'Contact': {
        'hi': 'संपर्क', 'ta': 'தொடர்பு', 'te': 'సంప్రదించండి', 'bn': 'যোগাযোগ',
        'mr': 'संपर्क', 'gu': 'સંપર્ક', 'kn': 'ಸಂಪರ್ಕ', 'ml': 'ബന്ധപ്പെടുക',
        'es': 'Contacto', 'fr': 'Contact', 'de': 'Kontakt', 'ar': 'الاتصال'
    },
    'Actions': {
        'hi': 'कार्रवाई', 'ta': 'செயல்கள்', 'te': 'చర్యలు', 'bn': 'পদক্ষেপ',
        'mr': 'कृती', 'gu': 'ક્રિયાઓ', 'kn': 'ಕ್ರಿಯೆಗಳು', 'ml': 'പ്രവർത്തനങ്ങൾ',
        'es': 'Acciones', 'fr': 'Actions', 'de': 'Aktionen', 'ar': 'الإجراءات'
    },
    'Patient Information': {
        'hi': 'मरीज़ की जानकारी', 'ta': 'நோயாளி தகவல்', 'te': 'రోగి సమాచారం', 'bn': 'রোগীর তথ্য',
        'mr': 'रुग्णाची माहिती', 'gu': 'દર્દીની માહિતી', 'kn': 'ರೋಗಿಯ ಮಾಹಿತಿ', 'ml': 'രോഗിയുടെ വിവരങ്ങൾ',
        'es': 'Información del Paciente', 'fr': 'Informations sur le Patient', 'de': 'Patienteninformationen', 'ar': 'معلومات المريض'
    },
    'Full Name': {
        'hi': 'पूरा नाम', 'ta': 'முழுப் பெயர்', 'te': 'పూర్తి పేరు', 'bn': 'সম্পূর্ণ নাম',
        'mr': 'पूर्ण नाव', 'gu': 'પૂરું નામ', 'kn': 'ಪೂರ್ಣ ಹೆಸರು', 'ml': 'പൂർണ്ണ പേര്',
        'es': 'Nombre Completo', 'fr': 'Nom Complet', 'de': 'Vollständiger Name', 'ar': 'الاسم الكامل'
    },
    'Age & Gender': {
        'hi': 'आयु और लिंग', 'ta': 'வயது மற்றும் பாலினம்', 'te': 'వయస్సు & లింగం', 'bn': 'বয়স ও লিঙ্গ',
        'mr': 'वय आणि लिंग', 'gu': 'ઉંમર અને જાતિ', 'kn': 'ವಯಸ್ಸು ಮತ್ತು ಲಿಂಗ', 'ml': 'പ്രായവും ലിംഗവും',
        'es': 'Edad y Género', 'fr': 'Âge et Genre', 'de': 'Alter & Geschlecht', 'ar': 'العمر والجنس'
    },
    'Contact Number': {
        'hi': 'संपर्क नंबर', 'ta': 'தொடர்பு எண்', 'te': 'సంప్రదింపు సంఖ్య', 'bn': 'যোগাযোগের নম্বর',
        'mr': 'संपर्क क्रमांक', 'gu': 'સંપર્ક નંબર', 'kn': 'ಸಂಪರ್ಕ ಸಂಖ್ಯೆ', 'ml': 'ഫോൺ നമ്പർ',
        'es': 'Número de Contacto', 'fr': 'Numéro de Contact', 'de': 'Kontaktnummer', 'ar': 'رقم الاتصال'
    },
    'Emergency Contact': {
        'hi': 'आपातकालीन संपर्क', 'ta': 'அவசர தொடர்பு', 'te': 'అత్యవసర సంప్రదింపు', 'bn': 'জরুরী যোগাযোগ',
        'mr': 'तातडीचा संपर्क', 'gu': 'કટોકટી સંપર્ક', 'kn': 'ತುರ್ತು ಸಂಪರ್ಕ', 'ml': 'അടിയന്തര കോൺടാക്റ്റ്',
        'es': 'Contacto de Emergencia', 'fr': 'Contact d\'Urgence', 'de': 'Notfallkontakt', 'ar': 'جهة اتصال الطوارئ'
    },
    'Address': {
        'hi': 'पता', 'ta': 'முகவரி', 'te': 'చిరునామా', 'bn': 'ঠিকানা',
        'mr': 'पत्ता', 'gu': 'સરનામું', 'kn': 'ವಿಳಾಸ', 'ml': 'മേൽവിലാസം',
        'es': 'Dirección', 'fr': 'Adresse', 'de': 'Adresse', 'ar': 'العنوان'
    },
    'Registered': {
        'hi': 'पंजीकृत', 'ta': 'பதிவு செய்யப்பட்டது', 'te': 'నమోదైన తేదీ', 'bn': 'নিবন্ধিত',
        'mr': 'नोंदणीकृत', 'gu': 'નોંધાયેલ', 'kn': 'ನೋಂದಾಯಿಸಲಾಗಿದೆ', 'ml': 'രജിസ്റ്റർ ചെയ്തത്',
        'es': 'Registrado', 'fr': 'Enregistré', 'de': 'Registriert', 'ar': 'مسجل'
    },
    'Medical History': {
        'hi': 'चिकित्सा इतिहास', 'ta': 'மருத்துவ வரலாறு', 'te': 'వైద్య చరిత్ర', 'bn': 'চিকিৎসার ইতিহাস',
        'mr': 'वैद्यकीय इतिहास', 'gu': 'તબીબી ઇતિહાસ', 'kn': 'ವೈದ್ಯಕೀಯ ಇತಿಹಾಸ', 'ml': 'ചികിത്സാ ചരിത്രം',
        'es': 'Historial Médico', 'fr': 'Antécédents Médicaux', 'de': 'Krankengeschichte', 'ar': 'التاريخ الطبي'
    },
    'Known Allergies': {
        'hi': 'ज्ञात एलर्जी', 'ta': 'அறியப்பட்ட ஒவ்வாமைகள்', 'te': 'తెలిసిన అలర్జీలు', 'bn': 'জানা অ্যালার্জি',
        'mr': 'ज्ञात अ‍ॅलर्जी', 'gu': 'જાણીતી એલર્જી', 'kn': 'ತಿಳಿದಿರುವ ಅಲರ್ಜಿಗಳು', 'ml': 'അലർജികൾ',
        'es': 'Alergias Conocidas', 'fr': 'Allergies Connues', 'de': 'Bekannte Allergien', 'ar': 'الحساسية المعروفة'
    },
    'X-ray Analysis History': {
        'hi': 'एक्स-रे विश्लेषण इतिहास', 'ta': 'எக்ஸ்-ரே பகுப்பாய்வு வரலாறு', 'te': 'ఎక్స్-రే విశ్లేషణ చరిత్ర', 'bn': 'এক্স-রে বিশ্লেষণ ইতিহাস',
        'mr': 'क्ष-किरण विश्लेषण इतिहास', 'gu': 'એક્સ-રે વિશ્લેષણ ઇતિહાસ', 'kn': 'ಕ್ಷ-ಕಿರಣ ವಿಶ್ಲೇಷಣೆ ಇತಿಹಾಸ', 'ml': 'എക്സ്-റേ വിശകലന ചരിത്രം',
        'es': 'Historial de Análisis de Rayos X', 'fr': 'Historique des Analyses de Rayons X', 'de': 'Röntgenanalyse-Verlauf', 'ar': 'تاريخ تحليل الأشعة السينية'
    },
    'Compare Scans Timeline': {
        'hi': 'स्कैन समयरेखा की तुलना करें', 'ta': 'ஸ்கேன் காலவரிசையை ஒப்பிடுக', 'te': 'స్కాన్ టైమ్‌లైన్‌ను సరిపోల్చండి', 'bn': 'স্ক্যান টাইমলাইন তুলনা করুন',
        'mr': 'स्कॅन टाइमलाइन तुलना करा', 'gu': 'સ્કેન સમયરેખા સરખાવો', 'kn': 'ಸ್ಕ್ಯಾನ್ ಟೈಮ್‌ಲೈನ್ ಹೋಲಿಸಿ', 'ml': 'സ്കാൻ ടൈംലൈൻ താരതമ്യം ചെയ്യുക',
        'es': 'Comparar Línea de Tiempo de Escaneos', 'fr': 'Comparer la Chronologie des Analyses', 'de': 'Scan-Zeitachse vergleichen', 'ar': 'مقارنة الجدول الزمني للفحوصات'
    },
    'Total Scans': {
        'hi': 'कुल स्कैन', 'ta': 'மொத்த ஸ்கேன்கள்', 'te': 'మొత్తం స్కాన్లు', 'bn': 'মোট স্ক্যান',
        'mr': 'एकूण स्कॅन', 'gu': 'કુલ સ્કેન', 'kn': 'ಒಟ್ಟು ಸ್ಕ್ಯಾನ್‌ಗಳು', 'ml': 'ആകെ സ്കാനുകൾ',
        'es': 'Total de Escaneos', 'fr': 'Total des Analyses', 'de': 'Gesamtzahl der Scans', 'ar': 'إجمالي الفحوصات'
    },
    'Date': {
        'hi': 'दिनांक', 'ta': 'தேதி', 'te': 'తేదీ', 'bn': 'তারিখ',
        'mr': 'तारीख', 'gu': 'તારીખ', 'kn': 'ದಿನಾಂಕ', 'ml': 'തീയതി',
        'es': 'Fecha', 'fr': 'Date', 'de': 'Datum', 'ar': 'التاريخ'
    },
    'Body Part': {
        'hi': 'शरीर का अंग', 'ta': 'உடல் உறுப்பு', 'te': 'శరీర భాగం', 'bn': 'শরীরের অঙ্গ',
        'mr': 'शरीराचा अवयव', 'gu': 'શરીરનો ભાગ', 'kn': 'ದೇಹದ ಭಾಗ', 'ml': 'ശരീരഭാഗം',
        'es': 'Parte del Cuerpo', 'fr': 'Partie du Corps', 'de': 'Körperteil', 'ar': 'جزء من الجسم'
    },
    'Result': {
        'hi': 'परिणाम', 'ta': 'முடிவு', 'te': 'ఫలితం', 'bn': 'ফলাফল',
        'mr': 'निकाल', 'gu': 'પરિણામ', 'kn': 'ಫಲಿತಾಂಶ', 'ml': 'ഫലം',
        'es': 'Resultado', 'fr': 'Résultat', 'de': 'Ergebnis', 'ar': 'النتيجة'
    },
    'Confidence': {
        'hi': 'सटीकता / विश्वास स्तर', 'ta': 'நம்பகத்தன்மை', 'te': 'విశ్వాస స్థాయి', 'bn': 'নির্ভুলতা স্তর',
        'mr': 'विश्वास पातळी', 'gu': 'વિશ્વાસ સ્તર', 'kn': 'ವಿಶ್ವಾಸಾರ್ಹತೆ', 'ml': 'വിശ്വാസ്യത',
        'es': 'Confianza', 'fr': 'Confiance', 'de': 'Zuverlässigkeit', 'ar': 'مستوى الثقة'
    },
    'Analysis Summary': {
        'hi': 'विश्लेषण सारांश', 'ta': 'பகுப்பாய்வு சுருக்கம்', 'te': 'విశ్లేషణ సారాంశం', 'bn': 'বিশ্লেষণ সারাংশ',
        'mr': 'विश्लेषण सारांश', 'gu': 'વિશ્લેષણ સારાંશ', 'kn': 'ವಿಶ್ಲೇಷಣೆ ಸಾರಾಂಶ', 'ml': 'വിശകലന സംഗ്രഹം',
        'es': 'Resumen de Análisis', 'fr': 'Résumé de l\'Analyse', 'de': 'Analyseübersicht', 'ar': 'ملخص التحليل'
    },
    'Normal Results': {
        'hi': 'सामान्य परिणाम', 'ta': 'இயல்பான முடிவுகள்', 'te': 'సాధారణ ఫలితాలు', 'bn': 'স্বাভাবিক ফলাফল',
        'mr': 'सामान्य निकाल', 'gu': 'સામાન્ય પરિણામો', 'kn': 'ಸಾಮಾನ್ಯ ಫಲಿತಾಂಶಗಳು', 'ml': 'സാധാരണ ഫലങ്ങൾ',
        'es': 'Resultados Normales', 'fr': 'Résultats Normaux', 'de': 'Normale Befunde', 'ar': 'نتائج طبيعية'
    },
    'Abnormal Results': {
        'hi': 'असामान्य परिणाम', 'ta': 'இயல்புக்கு மாறான முடிவுகள்', 'te': 'అసాధారణ ఫలితాలు', 'bn': 'অস্বাভাবিক ফলাফল',
        'mr': 'असामान्य निकाल', 'gu': 'અસામાન્ય પરિણામો', 'kn': 'ಅಸಾಮಾನ್ಯ ಫಲಿತಾಂಶಗಳು', 'ml': 'അസാധാരണ ഫലങ്ങൾ',
        'es': 'Resultados Anormales', 'fr': 'Résultats Anormaux', 'de': 'Auffällige Befunde', 'ar': 'نتائج غير طبيعية'
    },
    'Avg. Confidence': {
        'hi': 'औसत सटीकता', 'ta': 'சராசரி நம்பகத்தன்மை', 'te': 'సగటు విశ్వాసం', 'bn': 'গড় নির্ভুলতা',
        'mr': 'सरासरी अचूकता', 'gu': 'સરેરાશ વિશ્વાસ', 'kn': 'ಸರಾಸರಿ ವಿಶ್ವಾಸಾರ್ಹತೆ', 'ml': 'ശരാശരി വിശ്വാസ്യത',
        'es': 'Confianza Promedio', 'fr': 'Confiance Moyenne', 'de': 'Durchschnittliche Zuverlässigkeit', 'ar': 'متوسط الثقة'
    },
    'Back to Dashboard': {
        'hi': 'डैशबोर्ड पर वापस जाएं', 'ta': 'டாஷ்போர்டிற்குத் திரும்பு', 'te': 'డాష్‌బోర్డ్‌కు తిరిగి వెళ్లండి', 'bn': 'ড্যাশবোর্ডে ফিরে যান',
        'mr': 'डॅशबोर्डवर परत जा', 'gu': 'ડેશબોર્ડ પર પાછા જાઓ', 'kn': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್‌ಗೆ ಹಿಂತಿರುಗಿ', 'ml': 'ഡാഷ്‌ബോർഡിലേക്ക് മടങ്ങുക',
        'es': 'Volver al Panel', 'fr': 'Retour au Tableau de Bord', 'de': 'Zurück zur Übersicht', 'ar': 'العودة إلى لوحة القيادة'
    },
    'No X-ray analyses yet': {
        'hi': 'अभी तक कोई एक्स-रे विश्लेषण नहीं', 'ta': 'இதுவரை எக்ஸ்-ரே பகுப்பாய்வு இல்லை', 'te': 'ఇంకా ఎక్స్-రే విశ్లేషణలు లేవు', 'bn': 'এখনও কোনো এক্স-রে বিশ্লেষণ নেই',
        'mr': 'अद्याप कोणतेही क्ष-किरण विश्लेषण नाही', 'gu': 'હજુ સુધી કોઈ એક્સ-રે વિશ્લેષણ નથી', 'kn': 'ಇನ್ನೂ ಯಾವುದೇ ಕ್ಷ-ಕಿರಣ ವಿಶ್ಲೇಷಣೆಗಳಿಲ್ಲ', 'ml': 'ഇതുവരെ എക്സ്-റേ വിശകലനം നടന്നിട്ടില്ല',
        'es': 'Aún no hay análisis de rayos X', 'fr': 'Aucune analyse de rayons X pour le moment', 'de': 'Noch keine Röntgenanalysen vorhanden', 'ar': 'لا توجد تحليلات أشعة سينية حتى الآن'
    },
    'Upload the first X-ray image to start analysis': {
        'hi': 'विश्लेषण शुरू करने के लिए पहली एक्स-रे छवि अपलोड करें', 'ta': 'பகுப்பாய்வைத் தொடங்க முதல் எக்ஸ்-ரே படத்தை பதிவேற்றவும்', 'te': 'విశ్లేషణను ప్రారంభించడానికి మొదటి ఎక్స్-రే చిత్రాన్ని అప్‌లోడ్ చేయండి', 'bn': 'বিশ্লেষণ শুরু করতে প্রথম এক্স-রে চিত্রটি আপলোড করুন',
        'mr': 'विश्लेषण सुरू करण्यासाठी पहिली क्ष-किरण प्रतिमा अपलोड करा', 'gu': 'વિશ્લેષણ શરૂ કરવા માટે પ્રથમ એક્સ-રે છબી અપલોડ કરો', 'kn': 'ವಿಶ್ಲೇಷಣೆಯನ್ನು ಪ್ರಾರಂಭಿಸಲು ಮೊದಲ ಕ್ಷ-ಕಿರಣ ಚಿತ್ರವನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ', 'ml': 'വിശകലനം ആരംഭിക്കാൻ ആദ്യ എക്സ്-റേ ചിത്രം അപ്‌ലോഡ് ചെയ്യുക',
        'es': 'Suba la primera imagen de rayos X para comenzar el análisis', 'fr': 'Téléchargez la première image de rayons X pour commencer l\'analyse', 'de': 'Laden Sie das erste Röntgenbild hoch, um mit der Analyse zu beginnen', 'ar': 'قم بتحميل أول صورة أشعة سينية لبدء التحليل'
    },
    'About MediScan AI': {
        'hi': 'MediScan AI के बारे में', 'ta': 'MediScan AI பற்றி', 'te': 'MediScan AI గురించి', 'bn': 'MediScan AI সম্পর্কে',
        'mr': 'MediScan AI बद्दल', 'gu': 'MediScan AI વિશે', 'kn': 'MediScan AI ಬಗ್ಗೆ', 'ml': 'MediScan AI-യെ കുറിച്ച്',
        'es': 'Acerca de MediScan AI', 'fr': 'À propos de MediScan AI', 'de': 'Über MediScan AI', 'ar': 'حول MediScan AI'
    },
    'Our Mission': {
        'hi': 'हमारा मिशन', 'ta': 'எங்கள் நோக்கம்', 'te': 'మా లక్ష్యం', 'bn': 'আমাদের লক্ষ্য',
        'mr': 'आमचे ध्येय', 'gu': 'અમારું મિશન', 'kn': 'ನಮ್ಮ ಧ್ಯೇಯ', 'ml': 'ഞങ്ങളുടെ ദൗത്യം',
        'es': 'Nuestra Misión', 'fr': 'Notre Mission', 'de': 'Unsere Mission', 'ar': 'مهمتنا'
    },
    'Our Vision': {
        'hi': 'हमारा दृष्टिकोण', 'ta': 'எங்கள் பார்வை', 'te': 'మా దృక్పథం', 'bn': 'আমাদের দৃষ্টিভঙ্গি',
        'mr': 'आमचा दृष्टिकोन', 'gu': 'અમારી દ્રષ્ટિ', 'kn': 'ನಮ್ಮ ದೃಷ್ಟಿಕೋನ', 'ml': 'ഞങ്ങളുടെ കാഴ്ചപ്പാട്',
        'es': 'Nuestra Visión', 'fr': 'Notre Vision', 'de': 'Unsere Vision', 'ar': 'رؤيتنا'
    },
    'Key Features': {
        'hi': 'मुख्य विशेषताएं', 'ta': 'முக்கிய அம்சங்கள்', 'te': 'ముఖ్య లక్షణాలు', 'bn': 'প্রধান বৈশিষ্ট্যসমূহ',
        'mr': 'प्रमुख वैशिष्ट्ये', 'gu': 'મુખ્ય વિશેષતાઓ', 'kn': 'ಪ್ರಮುಖ ವೈಶಿಷ್ಟ್ಯಗಳು', 'ml': 'പ്രധാന സവിശേഷതകൾ',
        'es': 'Características Clave', 'fr': 'Fonctionnalités Clés', 'de': 'Hauptmerkmale', 'ar': 'الميزات الرئيسية'
    },
    'Advanced AI Analysis': {
        'hi': 'उन्नत एआई विश्लेषण', 'ta': 'மேம்பட்ட AI பகுப்பாய்வு', 'te': 'అధునాతన AI విశ్లేషణ', 'bn': 'উন্নত এআই বিশ্লেষণ',
        'mr': 'प्रगत एआय विश्लेषण', 'gu': 'અદ્યતન AI વિશ્લેષણ', 'kn': 'ಸುಧಾರಿತ AI ವಿಶ್ಲೇಷಣೆ', 'ml': 'വിപുലമായ AI വിശകലനം',
        'es': 'Análisis de IA Avanzado', 'fr': 'Analyse IA Avancée', 'de': 'Erweiterte KI-Analyse', 'ar': 'تحليل ذكاء اصطناعي متقدم'
    },
    'Secure Platform': {
        'hi': 'सुरक्षित मंच', 'ta': 'பாதுகாப்பான தளம்', 'te': 'సురక్షిత వేదిక', 'bn': 'সুরক্ষিত প্ল্যাটফর্ম',
        'mr': 'सुरक्षित प्लॅटफॉर्म', 'gu': 'સુરક્ષિત પ્લેટફોર્મ', 'kn': 'ಸುರಕ್ಷಿತ ವೇದಿಕೆ', 'ml': 'സുരക്ഷിത പ്ലാറ്റ്‌ഫോം',
        'es': 'Plataforma Segura', 'fr': 'Plateforme Sécurisée', 'de': 'Sichere Plattform', 'ar': 'منصة آمنة'
    },
    'User-Friendly Interface': {
        'hi': 'उपयोगकर्ता के अनुकूल इंटरफेस', 'ta': 'பயன்படுத்த எளிதான இடைமுகம்', 'te': 'యూజర్-ఫ్రెండ్లీ ఇంటర్‌ఫేస్', 'bn': 'ব্যবহারকারী-বান্ধব ইন্টারফেস',
        'mr': 'वापरण्यास सोपा इंटरफेस', 'gu': 'વપરાશકર્તા મૈત્રીપૂર્ણ ઇન્ટરફેસ', 'kn': 'ಬಳಕೆದಾರ ಸ್ನೇಹಿ ಇಂಟರ್ಫೇಸ್', 'ml': 'ഉപയോക്തൃ സൗഹൃദ ഇന്റർഫേസ്',
        'es': 'Interfaz Fácil de Usar', 'fr': 'Interface Conviviale', 'de': 'Benutzerfreundliche Oberfläche', 'ar': 'واجهة سهلة الاستخدام'
    },
    'Get in Touch': {
        'hi': 'संपर्क करें', 'ta': 'தொடர்பு கொள்ளவும்', 'te': 'సంప్రదించండి', 'bn': 'যোগাযোগ করুন',
        'mr': 'संपर्क साधा', 'gu': 'સંપર્કમાં રહો', 'kn': 'ಸಂಪರ್ಕದಲ್ಲಿರಿ', 'ml': 'ബന്ധപ്പെടുക',
        'es': 'Póngase en Contacto', 'fr': 'Contactez-nous', 'de': 'Kontakt aufnehmen', 'ar': 'تواصل معنا'
    },
    'Email': {
        'hi': 'ईमेल', 'ta': 'மின்னஞ்சல்', 'te': 'ఈమెయిల్', 'bn': 'ইমেল',
        'mr': 'ईमेल', 'gu': 'ઈમેલ', 'kn': 'ಇಮೇಲ್', 'ml': 'ഇമെയിൽ',
        'es': 'Correo Electrónico', 'fr': 'Email', 'de': 'E-Mail', 'ar': 'البريد الإلكتروني'
    },
    'Phone': {
        'hi': 'फ़ोन', 'ta': 'தொலைபேசி', 'te': 'ఫోన్', 'bn': 'ফোন',
        'mr': 'फोन', 'gu': 'ફોન', 'kn': 'ದೂರವಾಣಿ', 'ml': 'ഫോൺ',
        'es': 'Teléfono', 'fr': 'Téléphone', 'de': 'Telefon', 'ar': 'الهاتف'
    },
    'Location': {
        'hi': 'स्थान', 'ta': 'இருப்பிடம்', 'te': 'ప్రాంతం', 'bn': 'অবস্থান',
        'mr': 'स्थान', 'gu': 'સ્થાન', 'kn': 'ಸ್ಥಳ', 'ml': 'സ്ഥലം',
        'es': 'Ubicación', 'fr': 'Emplacement', 'de': 'Standort', 'ar': 'الموقع'
    },
    'years': {
        'hi': 'वर्ष', 'ta': 'ஆண்டுகள்', 'te': 'సంవత్సరాలు', 'bn': 'বছর',
        'mr': 'वर्षे', 'gu': 'વર્ષ', 'kn': 'ವರ್ಷಗಳು', 'ml': 'വർഷം',
        'es': 'años', 'fr': 'ans', 'de': 'Jahre', 'ar': 'سنوات'
    },
    'Not specified': {
        'hi': 'निर्दिष्ट नहीं', 'ta': 'குறிப்பிடப்படவில்லை', 'te': 'పేర్కొనబడలేదు', 'bn': 'নির্দিষ্ট করা নেই',
        'mr': 'नमूद केलेले नाही', 'gu': 'સ્પષ્ટ કરેલ નથી', 'kn': 'ನಿರ್ದಿಷ್ಟಪಡಿಸಿಲ್ಲ', 'ml': 'വ്യക്തമാക്കിയിട്ടില്ല',
        'es': 'No especificado', 'fr': 'Non spécifié', 'de': 'Nicht angegeben', 'ar': 'غير محدد'
    },
    'Contact Us': {
        'hi': 'हमसे संपर्क करें', 'ta': 'எங்களை தொடர்பு கொள்ளவும்', 'te': 'మమ్మల్ని సంప్రదించండి', 'bn': 'আমাদের সাথে যোগাযোগ করুন',
        'mr': 'आमच्याशी संपर्क साधा', 'gu': 'અમારો સંપર્ક કરો', 'kn': 'ನಮ್ಮನ್ನು ಸಂಪರ್ಕಿಸಿ', 'ml': 'ഞങ്ങളെ ബന്ധപ്പെടുക',
        'es': 'Contáctenos', 'fr': 'Contactez-nous', 'de': 'Kontaktieren Sie uns', 'ar': 'اتصل بنا'
    }
}


class TranslationService:
    def __init__(self):
        self.supported_languages = SUPPORTED_LANGUAGES
        self.static_dict = STATIC_DICTIONARY
        self.cache = {}
        self.cache_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'translation_cache.json')
        self._translator = None
        self.load_cache()
        # Register graceful exit to persist cache
        atexit.register(self.save_cache)

    @property
    def translator(self):
        """Lazy-load googletrans instance"""
        if self._translator is None:
            try:
                from googletrans import Translator
                self._translator = Translator()
            except Exception as e:
                logger.warning(f"Google Translator initialization deferred/failed: {e}")
                self._translator = None
        return self._translator

    def load_cache(self):
        """Load translation cache from file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading translation cache: {e}")
            self.cache = {}

    def save_cache(self):
        """Save translation cache to file safely"""
        try:
            if self.cache:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Error saving translation cache: {e}")

    def translate_text(self, text, target_language='en', source_language='auto'):
        """Translate text to target language with fast-path dictionary, memory cache, and Google Translate fallback"""
        if not text:
            return text

        if isinstance(text, (int, float, bool)):
            return str(text)

        text_str = str(text).strip()
        if not text_str:
            return text

        if target_language == 'en' or target_language not in self.supported_languages:
            return text_str

        # 1. Check curated static dictionary
        if text_str in self.static_dict:
            lang_dict = self.static_dict[text_str]
            if target_language in lang_dict:
                return lang_dict[target_language]

        # Check case-insensitive match in static dictionary
        for orig_key, trans_map in self.static_dict.items():
            if orig_key.lower() == text_str.lower():
                if target_language in trans_map:
                    return trans_map[target_language]

        # 2. Check disk / memory cache
        cache_key = f"{text_str}_{source_language}_{target_language}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # 3. Dynamic Google Translate lookup
        trans_client = self.translator
        if trans_client:
            try:
                res = trans_client.translate(text_str, dest=target_language, src=source_language)
                translated_text = res.text
                if translated_text:
                    self.cache[cache_key] = translated_text
                    if len(self.cache) % 15 == 0:
                        self.save_cache()
                    return translated_text
            except Exception as e:
                logger.warning(f"Googletrans lookup error for '{text_str}' -> {target_language}: {e}")

        # Fallback to original text if translation unavailable
        return text_str

    def translate_dict(self, data_dict, target_language='en'):
        """Recursively translate dictionary values"""
        if target_language == 'en' or not data_dict:
            return data_dict

        translated_dict = {}
        for key, value in data_dict.items():
            if isinstance(value, str):
                translated_dict[key] = self.translate_text(value, target_language)
            elif isinstance(value, list):
                translated_dict[key] = [
                    self.translate_text(item, target_language) if isinstance(item, str) else item
                    for item in value
                ]
            elif isinstance(value, dict):
                translated_dict[key] = self.translate_dict(value, target_language)
            else:
                translated_dict[key] = value

        return translated_dict

    def translate_list(self, items, target_language='en'):
        """Translate a list of strings"""
        if target_language == 'en' or not items:
            return items
        return [self.translate_text(item, target_language) if isinstance(item, str) else item for item in items]

    def get_supported_languages(self):
        """Get dict of supported languages with metadata"""
        return self.supported_languages

    def get_language_name(self, language_code):
        """Get readable language name"""
        info = self.supported_languages.get(language_code)
        if isinstance(info, dict):
            return f"{info.get('native', info.get('name'))} ({info.get('name')})"
        return self.supported_languages.get(language_code, language_code)

    def detect_language(self, text):
        """Detect language of text"""
        if not text:
            return 'en'
        trans_client = self.translator
        if trans_client:
            try:
                res = trans_client.detect(text)
                return res.lang
            except Exception:
                pass
        return 'en'


# Global singleton instances for direct import
translation_service = TranslationService()
translator = translation_service
