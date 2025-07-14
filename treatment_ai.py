import random
from datetime import datetime
import pandas as pd
from treatment_plans import CONDITIONS, get_treatment_plan
import streamlit as st

class TreatmentAI:
    def __init__(self):
        self.patient_history = pd.DataFrame(columns=[
            'patient_id', 'visit_date', 'diagnosis', 'treatment', 'outcome'
        ])
        
    def generate_suggestions(self, diagnosis, patient_history=None):
        """Generate AI-enhanced treatment suggestions"""
        base_plan = get_treatment_plan(diagnosis, "SA Residents")
        
        try:
            # Simulate AI analysis (in real implementation, this would call an AI API)
            suggestions = {
                "standard_plan": base_plan,
                "ai_recommendations": self._generate_ai_recommendations(diagnosis, patient_history),
                "cost_saving_options": self._find_cost_saving_options(diagnosis),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            return suggestions
        except Exception as e:
            st.error(f"AI suggestion failed: {str(e)}")
            return {
                "standard_plan": base_plan,
                "error": "AI service unavailable - showing standard protocol"
            }
    
    def _generate_ai_recommendations(self, diagnosis, patient_history):
        """Generate simulated AI recommendations"""
        recommendations = []
        
        # Example rule-based suggestions
        if diagnosis == "Hypertension":
            recommendations.append({
                "type": "Lifestyle Adjustment",
                "recommendation": "Consider DASH diet and 30-min daily exercise",
                "evidence": "Clinical studies show 8-14mmHg reduction"
            })
            
        if diagnosis == "Type 2 Diabetes":
            recommendations.append({
                "type": "Medication Adjustment",
                "recommendation": "Consider adding SGLT2 inhibitor if HbA1c > 8%",
                "evidence": "Reduces cardiovascular risk by 30%"
            })
            
        # Add random simulated recommendations if none matched
        if not recommendations:
            options = [
                "Consider genetic testing for drug metabolism",
                "Review potential drug interactions",
                "Recommend follow-up in 2 weeks",
                "Consider telemedicine follow-up"
            ]
            recommendations.append({
                "type": "General Recommendation",
                "recommendation": random.choice(options),
                "evidence": "Based on similar patient profiles"
            })
            
        return recommendations
    
    def _find_cost_saving_options(self, diagnosis):
        """Identify cost-saving alternatives"""
        cost_options = []
        condition = CONDITIONS.get(diagnosis, {})
        
        if diagnosis == "Hypertension":
            cost_options.append({
                "option": "Use hydrochlorothiazide as first-line",
                "savings": "R120/month vs. amlodipine",
                "considerations": "Less effective in elderly"
            })
            
        if diagnosis == "Type 2 Diabetes":
            cost_options.append({
                "option": "Generic metformin instead of brand-name",
                "savings": "R80/month",
                "considerations": "Same active ingredient"
            })
            
        return cost_options or [{
            "option": "No specific cost-saving options identified",
            "savings": "",
            "considerations": "Standard protocol already cost-effective"
        }]

# Global instance
treatment_ai = TreatmentAI()

def generate_treatment_plan(diagnosis, patient_history=None):
    """Get AI-enhanced treatment plan with fallback"""
    try:
        return treatment_ai.generate_suggestions(diagnosis, patient_history)
    except Exception:
        return get_treatment_plan(diagnosis, "SA Residents")