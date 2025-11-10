import os
from googletrans import Translator
import json
import time

class TranslationService:
    def __init__(self):
        self.translator = Translator()
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
        self.cache = {}
        self.cache_file = 'translation_cache.json'
        self.load_cache()
    
    def load_cache(self):
        """Load translation cache from file"""
        try:
            if os.path.exists(self.cache_file):
                import builtins
                with builtins.open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except Exception as e:
            print(f"Error loading translation cache: {e}")
            self.cache = {}
    
    def save_cache(self):
        """Save translation cache to file"""
        try:
            import builtins
            with builtins.open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving translation cache: {e}")
    
    def translate_text(self, text, target_language='en', source_language='auto'):
        """Translate text to target language"""
        if not text or target_language == 'en':
            return text
        
        # Create cache key
        cache_key = f"{text}_{source_language}_{target_language}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Translate using Google Translate
            result = self.translator.translate(text, dest=target_language, src=source_language)
            translated_text = result.text
            
            # Cache the result
            self.cache[cache_key] = translated_text
            
            # Save cache periodically
            if len(self.cache) % 10 == 0:
                self.save_cache()
            
            return translated_text
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_dict(self, data_dict, target_language='en'):
        """Translate dictionary values"""
        if target_language == 'en':
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
            else:
                translated_dict[key] = value
        
        return translated_dict
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return self.supported_languages
    
    def detect_language(self, text):
        """Detect language of text"""
        try:
            result = self.translator.detect(text)
            return result.lang
        except Exception as e:
            print(f"Language detection error: {e}")
            return 'en'
    
    def translate_medical_terms(self, terms, target_language='en'):
        """Translate medical terms with better accuracy"""
        if target_language == 'en':
            return terms
        
        translated_terms = []
        for term in terms:
            # Add medical context for better translation
            context_text = f"Medical condition: {term}"
            translated = self.translate_text(context_text, target_language)
            # Extract the translated term (remove "Medical condition: " prefix)
            if translated.startswith("Medical condition: "):
                translated = translated[19:]  # Remove prefix
            elif ":" in translated:
                translated = translated.split(":", 1)[1].strip()
            
            translated_terms.append(translated)
        
        return translated_terms
    
    def get_language_name(self, language_code):
        """Get language name from code"""
        return self.supported_languages.get(language_code, language_code)
    
    def __del__(self):
        """Save cache when object is destroyed"""
        self.save_cache()
