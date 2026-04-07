"""
Risk Breakdown Calculator
Analyzes individual risk factor contributions
"""

import numpy as np

def calculate_risk_breakdown(clinical_data, clinical_prob, retinal_prob, fusion_prob):
    """
    Calculate individual feature contributions to hypertension risk.
    
    Uses rule-based approach to estimate how much each factor contributes.
    
    Args:
        clinical_data: Dict with all clinical features
        clinical_prob: Clinical model probability
        retinal_prob: Retinal model probability
        fusion_prob: Final fused probability
        
    Returns:
        Dict with detailed breakdown analysis
    """
    
    # Extract values
    age = clinical_data.get('age', 50)
    sex = clinical_data.get('sex', 0)
    bmi = clinical_data.get('bmi', 25)
    systolic_bp = clinical_data.get('systolic_bp', 120)
    diastolic_bp = clinical_data.get('diastolic_bp', 80)
    glucose = clinical_data.get('glucose', 100)
    totChol = clinical_data.get('totChol', 200)
    heartRate = clinical_data.get('heartRate', 75)
    currentSmoker = clinical_data.get('currentSmoker', 0)
    diabetes = clinical_data.get('diabetes', 0)
    BPMeds = clinical_data.get('BPMeds', 0)
    
    # Calculate individual factor scores (0-1 scale)
    factors = {}
    
    # 1. Blood Pressure (most important)
    systolic_score = min(max(systolic_bp - 120, 0) / 60, 1.0)  # 120-180 range
    diastolic_score = min(max(diastolic_bp - 80, 0) / 40, 1.0)  # 80-120 range
    bp_score = (systolic_score * 0.6 + diastolic_score * 0.4)  # Systolic weighted more
    factors['blood_pressure'] = bp_score
    
    # 2. Glucose
    glucose_score = min(max(glucose - 100, 0) / 200, 1.0)  # 100-300 range
    factors['glucose'] = glucose_score
    
    # 3. BMI
    bmi_score = min(max(bmi - 25, 0) / 15, 1.0)  # 25-40 range
    factors['bmi'] = bmi_score
    
    # 4. Age (non-modifiable)
    age_score = min(max(age - 40, 0) / 40, 1.0)  # 40-80 range
    factors['age'] = age_score
    
    # 5. Smoking (binary but high impact)
    smoking_score = 0.7 if currentSmoker == 1 else 0.0
    factors['smoking'] = smoking_score
    
    # 6. Diabetes (binary but high impact)
    diabetes_score = 0.6 if diabetes == 1 else 0.0
    factors['diabetes'] = diabetes_score
    
    # 7. Cholesterol
    chol_score = min(max(totChol - 200, 0) / 100, 1.0)  # 200-300 range
    factors['cholesterol'] = chol_score
    
    # 8. Heart Rate
    hr_excess = abs(heartRate - 75)  # Deviation from normal
    hr_score = min(hr_excess / 50, 1.0)  # Up to 50 bpm deviation
    factors['heart_rate'] = hr_score
    
    # 9. BP Medications (indicates existing condition)
    bpmeds_score = 0.5 if BPMeds == 1 else 0.0
    factors['bp_medications'] = bpmeds_score
    
    # 10. Sex (non-modifiable, males higher risk)
    sex_score = 0.3 if sex == 1 else 0.0  # Male = 1
    factors['sex'] = sex_score
    
    # Normalize to percentages (sum to 100%)
    total_score = sum(factors.values())
    if total_score > 0:
        factor_percentages = {k: (v / total_score) * 100 for k, v in factors.items()}
    else:
        factor_percentages = {k: 0 for k in factors.keys()}
    
    # Sort by contribution (highest first)
    sorted_factors = sorted(factor_percentages.items(), key=lambda x: x[1], reverse=True)
    
    # Determine modifiable vs non-modifiable
    modifiable_info = {
        'blood_pressure': {'value': systolic_bp, 'current': f'{systolic_bp}/{diastolic_bp} mmHg', 'healthy': '<120/80 mmHg'},
        'glucose': {'value': glucose, 'current': f'{glucose} mg/dL', 'healthy': '<100 mg/dL'},
        'bmi': {'value': bmi, 'current': f'{bmi:.1f}', 'healthy': '18.5-24.9'},
        'smoking': {'value': currentSmoker, 'current': 'Yes' if currentSmoker else 'No', 'healthy': 'No'},
        'diabetes': {'value': diabetes, 'current': 'Yes' if diabetes else 'No', 'healthy': 'No'},
        'cholesterol': {'value': totChol, 'current': f'{totChol} mg/dL', 'healthy': '<200 mg/dL'},
        'heart_rate': {'value': heartRate, 'current': f'{heartRate} bpm', 'healthy': '60-100 bpm'},
        'bp_medications': {'value': BPMeds, 'current': 'Yes' if BPMeds else 'No', 'healthy': 'No'}
    }
    
    non_modifiable_info = {
        'age': {'value': age, 'current': f'{age} years', 'impact': 'Unavoidable'},
        'sex': {'value': sex, 'current': 'Male' if sex == 1 else 'Female', 'impact': 'Genetic'}
    }
    
    # Build modifiable and non-modifiable lists for frontend
    modifiable_factors = []
    non_modifiable_factors = []
    
    for factor_name, contribution in sorted_factors:
        if factor_name in non_modifiable_info:
            non_modifiable_factors.append({
                'name': factor_name.replace('_', ' ').title(),
                'contribution': round(contribution, 1),
                'info': non_modifiable_info[factor_name]
            })
        else:
            modifiable_factors.append({
                'name': factor_name.replace('_', ' ').title(),
                'contribution': round(contribution, 1),
                'info': modifiable_info[factor_name]
            })
    
    # Generate top 3 recommendations
    recommendations = generate_recommendations(clinical_data, sorted_factors)
    
    # Calculate potential risk reduction
    risk_reduction = calculate_potential_reduction(clinical_data, sorted_factors)
    
    return {
        'overall_risk': float(fusion_prob),
        'risk_category': categorize_risk(fusion_prob),
        'factor_contributions': dict(sorted_factors),
        'modifiable_factors': modifiable_factors,
        'non_modifiable_factors': non_modifiable_factors,
        'top_recommendations': recommendations,
        'potential_risk_reduction': risk_reduction,
        'model_breakdown': {
            'clinical': float(clinical_prob),
            'retinal': float(retinal_prob),
            'fusion': float(fusion_prob)
        }
    }


def categorize_risk(prob):
    """Categorize risk level"""
    if prob < 0.3:
        return 'Low Risk'
    elif prob < 0.6:
        return 'Medium Risk'
    else:
        return 'High Risk'


def generate_recommendations(data, sorted_factors):
    """Generate top 3 priority recommendations"""
    recommendations = []
    
    # Get top 3 modifiable factors
    modifiable_factors = [
        f for f in sorted_factors 
        if f[0] not in ['age', 'sex'] and f[1] > 5  # Only if contributes >5%
    ][:3]
    
    for factor, contribution in modifiable_factors:
        rec = {
            'factor': factor.replace('_', ' ').title(),
            'contribution': round(contribution, 1),
            'impact': 'High' if contribution > 20 else 'Medium' if contribution > 10 else 'Low',
            'actions': get_actions(factor, data),
            'expected_reduction': round(estimate_reduction(factor, contribution) * 100, 1)
        }
        recommendations.append(rec)
    
    return recommendations


def get_actions(factor, data):
    """Get specific actions for each factor"""
    actions = {
        'blood_pressure': [
            'Reduce sodium intake to <2,300 mg/day',
            'Exercise 150 minutes per week',
            'Maintain healthy weight',
            'Limit alcohol consumption',
            'Consult doctor about medication'
        ],
        'glucose': [
            'Monitor carbohydrate intake',
            'Get HbA1c test',
            'Exercise regularly',
            'Maintain healthy weight',
            'Consult endocrinologist'
        ],
        'bmi': [
            'Aim for 10-15 lbs weight loss',
            'Balanced diet with calorie deficit',
            'Regular cardio exercise',
            'Strength training 2-3x/week',
            'Consult nutritionist'
        ],
        'smoking': [
            '🚨 QUIT SMOKING - Highest impact!',
            'Join smoking cessation program',
            'Use nicotine replacement therapy',
            'Seek support groups',
            'Consult healthcare provider'
        ],
        'diabetes': [
            'Maintain HbA1c <7%',
            'Monitor blood sugar daily',
            'Follow diabetic diet plan',
            'Regular medication adherence',
            'Regular endocrinologist visits'
        ],
        'cholesterol': [
            'Reduce saturated fat intake',
            'Increase fiber consumption',
            'Consider statin therapy',
            'Regular lipid panel tests',
            'Exercise regularly'
        ],
        'heart_rate': [
            'Practice stress management',
            'Regular cardiovascular exercise',
            'Adequate sleep (7-9 hours)',
            'Limit caffeine intake',
            'Consult cardiologist if persistently high'
        ],
        'bp_medications': [
            'Take medications as prescribed',
            'Regular blood pressure monitoring',
            'Don\'t skip doses',
            'Report side effects to doctor',
            'Regular follow-up appointments'
        ]
    }
    
    return actions.get(factor, ['Consult healthcare provider'])


def estimate_reduction(factor, contribution):
    """Estimate potential risk reduction"""
    # Conservative estimates based on clinical literature
    reduction_potential = {
        'blood_pressure': 0.25,  # 25% reduction possible
        'glucose': 0.15,
        'bmi': 0.12,
        'smoking': 0.15,
        'diabetes': 0.10,
        'cholesterol': 0.08,
        'heart_rate': 0.05,
        'bp_medications': 0.20  # With proper adherence
    }
    
    base_reduction = reduction_potential.get(factor, 0.05)
    # Weight by contribution
    estimated = base_reduction * (contribution / 100) * 2
    
    return min(estimated, 0.30)  # Cap at 30%


def calculate_potential_reduction(data, sorted_factors):
    """Calculate total potential risk reduction"""
    # If user addresses top 3 factors
    top_3 = [f for f in sorted_factors if f[0] not in ['age', 'sex']][:3]
    
    total_reduction = 0
    for factor, contribution in top_3:
        total_reduction += estimate_reduction(factor, contribution)
    
    return {
        'total': round(min(total_reduction, 0.40) * 100, 1),  # Cap at 40% total reduction, convert to %
        'timeframe': '6-12 months with consistent effort'
    }
