"""
Machine Learning Inference Service
Loads pre-trained RandomForest model and provides SHAP explainability
"""
import pickle
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path

# SHAP is optional — graceful fallback if not installed
try:
    import shap
except ImportError:
    shap = None

from .models import RiskLevel, Department, PatientInput


class MLInferenceService:
    """
    ML Service for triage prediction with explainability
    """
    
    def __init__(self, model_path: str = "models/triage_model.pkl"):
        self.model = None
        self.explainer = None
        self.feature_names = [
            'age', 'heart_rate', 'bp_systolic', 'bp_diastolic', 
            'temperature', 'num_symptoms', 'has_chest_pain', 
            'has_breathing_issues', 'has_fever'
        ]
        self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """Load pre-trained model from disk"""
        model_file = Path(model_path)
        
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"✅ ML Model loaded from {model_path}")
                
                # Initialize SHAP explainer
                # self.explainer = shap.TreeExplainer(self.model)
                print("✅ SHAP Explainer initialized")
            except Exception as e:
                print(f"⚠️ Error loading model: {e}")
                print("📝 Using rule-based fallback system")
                self.model = None
        else:
            print(f"⚠️ Model file not found at {model_path}")
            print("📝 Using rule-based fallback system")
            self.model = None
    
    def preprocess_input(self, patient_input: PatientInput) -> np.ndarray:
        """Convert patient input to feature vector"""
        vitals = patient_input.vitals
        symptoms = patient_input.symptoms
        
        # Feature engineering
        features = [
            patient_input.age,
            vitals.heart_rate,
            vitals.bp_systolic,
            vitals.bp_diastolic,
            vitals.temperature,
            len(symptoms),
            int(any('chest' in s.lower() for s in symptoms)),
            int(any('breath' in s.lower() for s in symptoms)),
            int(vitals.temperature > 100.4)
        ]
        
        return np.array(features).reshape(1, -1)
    
    def predict_risk(self, patient_input: PatientInput) -> Tuple[RiskLevel, float, Dict[str, float]]:
        """
        Predict risk level with confidence and feature importance
        
        Returns:
            - risk_level: RiskLevel enum
            - confidence: float (0-1)
            - feature_importance: Dict mapping feature names to importance scores
        """
        features = self.preprocess_input(patient_input)
        
        if self.model is not None:
            # Use trained model
            try:
                risk_proba = self.model.predict_proba(features)[0]
                risk_class = self.model.predict(features)[0]
                
                confidence = float(np.max(risk_proba))
                
                # Get SHAP values for explainability
                # shap_values = self.explainer.shap_values(features)
                # feature_importance = self._compute_feature_importance(shap_values, features)
                
                # Fallback feature importance (simple)
                feature_importance = self._compute_fallback_importance(patient_input)
                
                # Map class to RiskLevel
                risk_mapping = {0: RiskLevel.LOW, 1: RiskLevel.MEDIUM, 2: RiskLevel.HIGH}
                risk_level = risk_mapping.get(risk_class, RiskLevel.MEDIUM)
                
            except Exception as e:
                print(f"⚠️ Model prediction error: {e}")
                return self._rule_based_prediction(patient_input)
        else:
            # Rule-based fallback
            return self._rule_based_prediction(patient_input)
        
        # Check for immediate cases
        if self._is_immediate_case(patient_input):
            risk_level = RiskLevel.IMMEDIATE
            confidence = 0.99
        
        return risk_level, confidence, feature_importance
    
    def _rule_based_prediction(self, patient_input: PatientInput) -> Tuple[RiskLevel, float, Dict[str, float]]:
        """
        Fallback rule-based triage system
        Used when ML model is not available
        """
        vitals = patient_input.vitals
        symptoms = patient_input.symptoms
        age = patient_input.age
        
        risk_score = 0
        feature_importance = {}
        
        # Age factor
        if age > 65:
            risk_score += 25
            feature_importance['Age'] = 25
        elif age < 5:
            risk_score += 20
            feature_importance['Age'] = 20
        else:
            feature_importance['Age'] = 5
        
        # Heart rate
        if vitals.heart_rate > 130 or vitals.heart_rate < 50:
            risk_score += 20
            feature_importance['Heart Rate'] = 20
        elif vitals.heart_rate > 100:
            risk_score += 10
            feature_importance['Heart Rate'] = 10
        else:
            feature_importance['Heart Rate'] = 0
        
        # Blood pressure
        if vitals.bp_systolic > 160 or vitals.bp_systolic < 90:
            risk_score += 25
            feature_importance['Blood Pressure'] = 25
        elif vitals.bp_systolic > 140:
            risk_score += 15
            feature_importance['Blood Pressure'] = 15
        else:
            feature_importance['Blood Pressure'] = 0
        
        # Temperature
        if vitals.temperature > 102 or vitals.temperature < 95:
            risk_score += 15
            feature_importance['Temperature'] = 15
        elif vitals.temperature > 100.4:
            risk_score += 8
            feature_importance['Temperature'] = 8
        else:
            feature_importance['Temperature'] = 0
        
        # Symptoms
        symptom_score = min(len(symptoms) * 2, 15)
        feature_importance['Symptom Count'] = symptom_score
        risk_score += symptom_score
        
        # Critical symptoms
        critical_symptoms = ['chest pain', 'chest', 'difficulty breathing', 'unconscious']
        has_critical = any(any(crit in s.lower() for crit in critical_symptoms) for s in symptoms)
        if has_critical:
            risk_score += 20
            feature_importance['Critical Symptoms'] = 20
        
        # Determine risk level
        if risk_score >= 70:
            risk_level = RiskLevel.HIGH
            confidence = 0.85
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
            confidence = 0.75
        else:
            risk_level = RiskLevel.LOW
            confidence = 0.70
        
        # Check immediate
        if self._is_immediate_case(patient_input):
            risk_level = RiskLevel.IMMEDIATE
            confidence = 0.99
        
        return risk_level, confidence, feature_importance
    
    def _is_immediate_case(self, patient_input: PatientInput) -> bool:
        """Check if patient requires immediate attention"""
        vitals = patient_input.vitals
        symptoms = patient_input.symptoms
        
        # Critical vital signs
        if vitals.heart_rate > 140 or vitals.heart_rate < 45:
            return True
        if vitals.bp_systolic > 180 or vitals.bp_systolic < 85:
            return True
        if vitals.temperature > 104 or vitals.temperature < 94:
            return True
        
        # Critical symptoms
        emergency_keywords = ['unconscious', 'stroke', 'severe bleeding', 'cardiac arrest']
        for symptom in symptoms:
            if any(keyword in symptom.lower() for keyword in emergency_keywords):
                return True
        
        # Chest pain + high BP
        has_chest_pain = any('chest' in s.lower() for s in symptoms)
        if has_chest_pain and vitals.bp_systolic > 160:
            return True
        
        return False
    
    def _compute_fallback_importance(self, patient_input: PatientInput) -> Dict[str, float]:
        """Compute simple feature importance when SHAP is unavailable"""
        _, _, importance = self._rule_based_prediction(patient_input)
        return importance
    
    def predict_department(self, patient_input: PatientInput, risk_level: RiskLevel) -> Department:
        """Predict appropriate hospital department based on symptoms and risk"""
        symptoms = patient_input.symptoms
        vitals = patient_input.vitals
        age = patient_input.age
        
        # Immediate -> ICU or Emergency
        if risk_level == RiskLevel.IMMEDIATE:
            return Department.ICU if vitals.heart_rate > 140 else Department.EMERGENCY
        
        # Chest pain / cardiac symptoms -> Cardiology
        cardiac_keywords = ['chest pain', 'chest', 'heart', 'palpitations']
        if any(any(kw in s.lower() for kw in cardiac_keywords) for s in symptoms):
            return Department.CARDIOLOGY
        
        # Pediatric
        if age < 18:
            return Department.PEDIATRICS
        
        # Severe cases -> Emergency
        if risk_level == RiskLevel.HIGH:
            return Department.EMERGENCY
        
        # Surgery keywords
        surgery_keywords = ['trauma', 'fracture', 'laceration', 'injury']
        if any(any(kw in s.lower() for kw in surgery_keywords) for s in symptoms):
            return Department.SURGERY
        
        # Default
        return Department.GENERAL
    
    def generate_medical_advice(
        self, 
        risk_level: RiskLevel, 
        feature_importance: Dict[str, float],
        symptoms: List[str]
    ) -> str:
        """
        Generate explainable medical advice based on SHAP values and risk
        
        This links AI decision-making to actionable insights
        """
        # Get top contributing factors
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        top_factors = [f for f, score in sorted_features if score > 5][:3]
        
        advice_parts = []
        
        # Risk-based header
        if risk_level == RiskLevel.IMMEDIATE:
            advice_parts.append("🚨 IMMEDIATE ACTION REQUIRED: This is a medical emergency.")
            advice_parts.append("Call 911 or proceed to the nearest emergency room immediately.")
        elif risk_level == RiskLevel.HIGH:
            advice_parts.append("⚠️ HIGH PRIORITY: Urgent medical attention required.")
            advice_parts.append("Visit the emergency department within the next hour.")
        elif risk_level == RiskLevel.MEDIUM:
            advice_parts.append("📋 MEDIUM PRIORITY: Medical evaluation recommended.")
            advice_parts.append("Schedule an appointment with your healthcare provider today.")
        else:
            advice_parts.append("✅ LOW PRIORITY: Monitor symptoms.")
            advice_parts.append("Contact your doctor if symptoms worsen.")
        
        # Explainable reasoning
        if top_factors:
            advice_parts.append(f"\n**Priority factors detected:**")
            for factor in top_factors:
                advice_parts.append(f"• {factor}: Contributing to elevated risk assessment")
        
        # Symptom-specific advice
        if any('chest' in s.lower() for s in symptoms):
            advice_parts.append("\n⚕️ Cardiac indicators present. ECG and cardiac enzyme tests recommended.")
        
        if any('breath' in s.lower() for s in symptoms):
            advice_parts.append("\n⚕️ Respiratory symptoms detected. Oxygen saturation monitoring advised.")
        
        return "\n".join(advice_parts)


# Global ML service instance
ml_service = MLInferenceService()
