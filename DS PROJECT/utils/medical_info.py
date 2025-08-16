import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class MedicalInfoService:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        self.cache = {}
        self.medical_tips_db = self.load_medical_tips_db()
    
    def load_medical_tips_db(self):
        """Load local medical tips database"""
        return {
            'Normal': {
                'description': 'No abnormalities detected in the X-ray image.',
                'tips': [
                    'Maintain regular health checkups',
                    'Follow a balanced diet rich in calcium and vitamin D',
                    'Exercise regularly to maintain bone health',
                    'Avoid smoking and excessive alcohol consumption'
                ],
                'precautions': [
                    'Continue regular medical screenings',
                    'Report any new symptoms to your doctor'
                ]
            },
            'Pneumonia': {
                'description': 'Infection that inflames air sacs in one or both lungs.',
                'tips': [
                    'Get plenty of rest and sleep',
                    'Drink lots of fluids to help loosen secretions',
                    'Take prescribed antibiotics as directed',
                    'Use a humidifier or breathe steam from hot shower'
                ],
                'precautions': [
                    'Avoid smoking and secondhand smoke',
                    'Get vaccinated against pneumonia and flu',
                    'Wash hands frequently',
                    'Seek immediate medical attention if symptoms worsen'
                ]
            },
            'COVID-19': {
                'description': 'Respiratory illness caused by SARS-CoV-2 virus.',
                'tips': [
                    'Isolate yourself from others',
                    'Rest and stay hydrated',
                    'Monitor oxygen levels if possible',
                    'Take prescribed medications as directed'
                ],
                'precautions': [
                    'Wear masks when around others',
                    'Maintain social distancing',
                    'Disinfect surfaces regularly',
                    'Seek emergency care if breathing becomes difficult'
                ]
            },
            'Fracture': {
                'description': 'A break or crack in a bone.',
                'tips': [
                    'Keep the injured area immobilized',
                    'Apply ice to reduce swelling',
                    'Take pain medication as prescribed',
                    'Follow up with orthopedic specialist'
                ],
                'precautions': [
                    'Avoid putting weight on injured area',
                    'Keep cast or splint dry and clean',
                    'Watch for signs of infection',
                    'Attend all follow-up appointments'
                ]
            },
            'Arthritis': {
                'description': 'Inflammation of one or more joints causing pain and stiffness.',
                'tips': [
                    'Stay physically active with low-impact exercises',
                    'Maintain healthy weight to reduce joint stress',
                    'Apply heat or cold therapy as needed',
                    'Take anti-inflammatory medications as prescribed'
                ],
                'precautions': [
                    'Avoid high-impact activities',
                    'Use joint protection techniques',
                    'Monitor for medication side effects',
                    'Regular monitoring by rheumatologist'
                ]
            },
            'Tuberculosis': {
                'description': 'Bacterial infection that mainly affects the lungs.',
                'tips': [
                    'Take all prescribed medications consistently',
                    'Eat nutritious foods to boost immunity',
                    'Get plenty of rest',
                    'Avoid alcohol and smoking'
                ],
                'precautions': [
                    'Isolate until no longer contagious',
                    'Cover mouth when coughing or sneezing',
                    'Ensure good ventilation in living spaces',
                    'Complete entire course of treatment'
                ]
            }
        }
    
    def get_medical_info(self, condition, language='en'):
        """Get medical information for a condition"""
        # First check local database
        local_info = self.medical_tips_db.get(condition, {})
        
        if local_info:
            return {
                'condition': condition,
                'description': local_info.get('description', ''),
                'medical_tips': local_info.get('tips', []),
                'precautions': local_info.get('precautions', []),
                'source': 'local_database'
            }
        
        # If not found locally, try to search online
        return self.search_medical_info(condition)
    
    def search_medical_info(self, condition):
        """Search for medical information online"""
        if not self.google_api_key or not self.search_engine_id:
            return self.get_fallback_info(condition)
        
        try:
            # Search for medical information
            query = f"{condition} medical information symptoms treatment"
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': 3
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                if items:
                    # Extract information from search results
                    info = {
                        'condition': condition,
                        'description': f"Medical condition: {condition}",
                        'medical_tips': [
                            'Consult with a healthcare professional',
                            'Follow prescribed treatment plan',
                            'Monitor symptoms regularly'
                        ],
                        'precautions': [
                            'Seek immediate medical attention if symptoms worsen',
                            'Follow up with your doctor regularly'
                        ],
                        'source': 'online_search',
                        'references': [item.get('link', '') for item in items[:2]]
                    }
                    return info
            
        except Exception as e:
            print(f"Error searching medical info: {e}")
        
        return self.get_fallback_info(condition)
    
    def get_fallback_info(self, condition):
        """Get fallback medical information"""
        return {
            'condition': condition,
            'description': f"Medical condition detected: {condition}",
            'medical_tips': [
                'Consult with a qualified healthcare professional',
                'Follow prescribed treatment and medication',
                'Maintain regular follow-up appointments',
                'Adopt healthy lifestyle habits'
            ],
            'precautions': [
                'Do not ignore symptoms',
                'Seek immediate medical attention if condition worsens',
                'Follow medical advice strictly',
                'Keep emergency contacts readily available'
            ],
            'source': 'fallback'
        }
    
    def get_dietary_recommendations(self, condition):
        """Get dietary recommendations for a condition"""
        dietary_db = {
            'Pneumonia': [
                'Increase fluid intake (water, herbal teas)',
                'Consume protein-rich foods (lean meats, eggs, legumes)',
                'Eat antioxidant-rich fruits and vegetables',
                'Include probiotics (yogurt, kefir) to boost immunity'
            ],
            'Fracture': [
                'Increase calcium intake (dairy products, leafy greens)',
                'Consume vitamin D rich foods (fatty fish, fortified foods)',
                'Include protein for bone healing (lean meats, beans)',
                'Eat foods rich in vitamin C (citrus fruits, berries)'
            ],
            'Arthritis': [
                'Include anti-inflammatory foods (fatty fish, nuts)',
                'Consume antioxidant-rich fruits and vegetables',
                'Limit processed foods and sugar',
                'Include omega-3 fatty acids (salmon, walnuts)'
            ]
        }
        
        return dietary_db.get(condition, [
            'Maintain a balanced, nutritious diet',
            'Stay hydrated',
            'Consult with a nutritionist for personalized advice'
        ])
    
    def get_exercise_recommendations(self, condition):
        """Get exercise recommendations for a condition"""
        exercise_db = {
            'Normal': [
                'Regular cardio exercises (walking, swimming)',
                'Strength training 2-3 times per week',
                'Flexibility and stretching exercises',
                'Maintain active lifestyle'
            ],
            'Arthritis': [
                'Low-impact exercises (swimming, cycling)',
                'Range of motion exercises',
                'Gentle stretching and yoga',
                'Avoid high-impact activities'
            ],
            'Fracture': [
                'Follow physical therapy recommendations',
                'Gradual return to activity as healing progresses',
                'Avoid activities that stress the injured area',
                'Focus on maintaining fitness in unaffected areas'
            ]
        }
        
        return exercise_db.get(condition, [
            'Consult with healthcare provider before starting exercise',
            'Start slowly and gradually increase intensity',
            'Listen to your body and rest when needed'
        ])
