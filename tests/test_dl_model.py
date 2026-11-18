import os
try:
    import pytest
except ImportError:
    pytest = None
from utils.enhanced_ml_model import EnhancedMLPredictor

def test_enhanced_ml_predictor_loads_dl_models():
    predictor = EnhancedMLPredictor()
    assert predictor.chest_model is not None, "Chest ResNet-18 model was not loaded!"
    assert predictor.bone_model is not None, "Bone ResNet-18 model was not loaded!"

def test_chest_prediction_with_deep_learning():
    predictor = EnhancedMLPredictor()
    sample_img = os.path.join(r'.\dataset', 'COVID-19_Radiography_Dataset', 'COVID', 'images', 'COVID-1.png')
    if os.path.exists(sample_img):
        cond, conf, details = predictor.predict(sample_img, body_part='chest')
        assert cond == 'COVID-19'
        assert conf >= 0.65
        assert 'ResNet-18' in details['ai_model_used']
        assert os.path.exists(os.path.join(os.path.dirname(sample_img), details['heatmap_image']))

def test_bone_prediction_with_deep_learning():
    predictor = EnhancedMLPredictor()
    sample_img = os.path.join(r'.\dataset', 'Bone_Fracture_Binary_Classification', 'Bone_Fracture_Binary_Classification', 'test', 'not fractured', '1.png')
    if os.path.exists(sample_img):
        cond, conf, details = predictor.predict(sample_img, body_part='hand')
        assert cond == 'Normal'
        assert conf > 0.65
        assert 'ResNet-18' in details['ai_model_used']
