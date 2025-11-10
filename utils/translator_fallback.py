class TranslationService:
    def __init__(self):
        self.supported_languages = {
            'en': 'English',
            'hi': 'Hindi',
            'ta': 'Tamil',
            'te': 'Telugu',
            'bn': 'Bengali',
            'mr': 'Marathi',
            'gu': 'Gujarati',
            'kn': 'Kannada',
            'ml': 'Malayalam',
            'pa': 'Punjabi',
            'ur': 'Urdu',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic'
        }
    
    def translate_text(self, text, target_language='en', source_language='auto'):
        return text  # Return original text
    
    def translate_dict(self, data_dict, target_language='en'):
        return data_dict  # Return original dict
    
    def get_supported_languages(self):
        return self.supported_languages
    
    def detect_language(self, text):
        return 'en'
    
    def translate_medical_terms(self, terms, target_language='en'):
        return terms
    
    def get_language_name(self, language_code):
        return self.supported_languages.get(language_code, language_code)