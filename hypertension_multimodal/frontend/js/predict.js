// HyperRNet - Prediction Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Get DOM elements
    const clinicalForm = document.getElementById('clinical-form');
    const retinalImageInput = document.getElementById('retinal-image');
    const imagePreview = document.querySelector('.image-preview');
    const predictBtn = document.querySelector('.predict-btn');
    const resultsCard = document.querySelector('.results-card');
    
    // Form input elements - using IDs for reliability
    const ageInput = document.getElementById('age-input');
    const bmiInput = document.getElementById('bmi-input');
    const systolicBPInput = document.getElementById('systolic-input');
    const diastolicBPInput = document.getElementById('diastolic-input');
    const glucoseInput = document.getElementById('glucose-input');
    const smokingSelect = document.getElementById('smoking-status');
    const diabetesSelect = document.getElementById('diabetes');
    
    // Optional fields (for improved version compatibility)
    const sexSelect = document.getElementById('sex');
    const cholesterolInput = document.getElementById('cholesterol-input');
    const heartRateInput = document.getElementById('heart-rate-input');
    const bpMedsSelect = document.getElementById('bp-meds');
    
    // Store uploaded image
    let uploadedImage = null;
    
    // Image Upload Handler
    retinalImageInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        
        if (file) {
            // Validate file type
            if (!file.type.startsWith('image/')) {
                showError('Please upload a valid image file');
                return;
            }
            
            // Validate file size (max 5MB)
            if (file.size > 5 * 1024 * 1024) {
                showError('Image size must be less than 5MB');
                return;
            }
            
            uploadedImage = file;
            
            // Create image preview
            const reader = new FileReader();
            reader.onload = function(event) {
                imagePreview.innerHTML = `
                    <img src="${event.target.result}" alt="Retinal Fundus Preview" 
                         style="max-width: 100%; max-height: 200px; border-radius: 8px; object-fit: contain;">
                `;
            };
            reader.readAsDataURL(file);
        }
    });
    
    // Predict Button Click Handler
    predictBtn.addEventListener('click', async function() {
        
        // Validate all inputs
        if (!validateForm()) {
            return;
        }
        
        // Show loading state
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<span style="display: inline-flex; align-items: center; gap: 8px;">Processing... <span class="spinner"></span></span>';
        
        // Collect form data (works with both current and improved HTML)
        const formData = {
            age: parseFloat(ageInput.value),
            bmi: parseFloat(bmiInput.value),
            systolic_bp: parseFloat(systolicBPInput.value),
            diastolic_bp: parseFloat(diastolicBPInput.value),
            glucose: parseFloat(glucoseInput.value),
            smoking: parseInt(smokingSelect.value),
            diabetes: parseInt(diabetesSelect.value),
            // Optional fields (only if present in improved HTML)
            sex: sexSelect && sexSelect.value ? parseInt(sexSelect.value) : null,
            cholesterol: cholesterolInput && cholesterolInput.value ? parseFloat(cholesterolInput.value) : null,
            heartRate: heartRateInput && heartRateInput.value ? parseInt(heartRateInput.value) : null,
            bpMeds: bpMedsSelect && bpMedsSelect.value ? parseInt(bpMedsSelect.value) : null
        };
        
        try {
            // Call API
            const result = await predictRisk(formData, uploadedImage);
            
            // Display results
            displayResults(result);
            
            // Scroll to results
            resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            
        } catch (error) {
            showError('Prediction failed. Please try again.');
            console.error('Prediction error:', error);
        } finally {
            // Reset button state
            predictBtn.disabled = false;
            predictBtn.innerHTML = 'Predict Risk';
        }
    });
    
    // Form Validation
    function validateForm() {
        // Check all clinical data fields are filled
        if (!ageInput.value || !bmiInput.value || !systolicBPInput.value || 
            !diastolicBPInput.value || !glucoseInput.value) {
            showError('Please fill in all clinical data fields');
            return false;
        }
        
        // Validate age range
        const age = parseFloat(ageInput.value);
        if (age < 18 || age > 120) {
            showError('Age must be between 18 and 120');
            return false;
        }
        
        // Validate BMI range
        const bmi = parseFloat(bmiInput.value);
        if (bmi < 10 || bmi > 60) {
            showError('BMI must be between 10 and 60');
            return false;
        }
        
        // Validate BP ranges
        const systolic = parseFloat(systolicBPInput.value);
        const diastolic = parseFloat(diastolicBPInput.value);
        
        if (systolic < 70 || systolic > 250) {
            showError('Systolic BP must be between 70 and 250');
            return false;
        }
        
        if (diastolic < 40 || diastolic > 150) {
            showError('Diastolic BP must be between 40 and 150');
            return false;
        }
        
        if (systolic <= diastolic) {
            showError('Systolic BP must be greater than Diastolic BP');
            return false;
        }
        
        // Validate glucose level
        const glucose = parseFloat(glucoseInput.value);
        if (glucose < 50 || glucose > 400) {
            showError('Glucose level must be between 50 and 400 mg/dL');
            return false;
        }
        
        // Check dropdown selections
        if (smokingSelect.value === '' || diabetesSelect.value === '') {
            showError('Please select smoking and diabetes status');
            return false;
        }
        
        // Check image upload
        if (!uploadedImage) {
            showError('Please upload a retinal fundus image');
            return false;
        }
        
        return true;
    }
    
    // Prediction API Call
    async function predictRisk(clinicalData, imageFile) {
        const formData = new FormData();
        
        // Append all clinical data (always present)
        formData.append("age", clinicalData.age);
        formData.append("bmi", clinicalData.bmi);
        formData.append("systolic_bp", clinicalData.systolic_bp);
        formData.append("diastolic_bp", clinicalData.diastolic_bp);
        formData.append("glucose", clinicalData.glucose);
        
        // Append smoking and diabetes (already collected in form!)
        formData.append("currentSmoker", clinicalData.smoking);
        formData.append("diabetes", clinicalData.diabetes);
        
        // Set cigsPerDay based on smoking status (estimate 10 if smoker)
        formData.append("cigsPerDay", clinicalData.smoking === 1 ? 10 : 0);
        
        // Append optional fields if available (for improved form compatibility)
        if (clinicalData.sex !== undefined && clinicalData.sex !== null) {
            formData.append("sex", clinicalData.sex);
        }
        
        if (clinicalData.cholesterol !== undefined && clinicalData.cholesterol !== null) {
            formData.append("totChol", clinicalData.cholesterol);
        }
        
        if (clinicalData.heartRate !== undefined && clinicalData.heartRate !== null) {
            formData.append("heartRate", clinicalData.heartRate);
        }
        
        if (clinicalData.bpMeds !== undefined && clinicalData.bpMeds !== null) {
            formData.append("BPMeds", clinicalData.bpMeds);
        }
        
        // Note: Any missing fields will use backend defaults
        
        // Append image file
        formData.append("fundus_image", imageFile);
        
        console.log('Sending prediction request...');
        console.log('Clinical data:', clinicalData);
        console.log('Image file:', imageFile.name, imageFile.size, 'bytes');
        console.log('Fields sent:', {
            age: clinicalData.age,
            sex: clinicalData.sex || 'using default',
            bmi: clinicalData.bmi,
            systolic_bp: clinicalData.systolic_bp,
            diastolic_bp: clinicalData.diastolic_bp,
            glucose: clinicalData.glucose,
            totChol: clinicalData.cholesterol || 'using default',
            heartRate: clinicalData.heartRate || 'using default',
            currentSmoker: clinicalData.smoking,
            cigsPerDay: clinicalData.smoking === 1 ? 10 : 0,
            diabetes: clinicalData.diabetes,
            BPMeds: clinicalData.bpMeds || 'using default'
        });
        
        const response = await fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            body: formData
        });
        
        console.log('Response status:', response.status);
        
        // Get the response data regardless of status
        const data = await response.json();
        console.log('Response data:', data);
        
        // If there's an error in the response, show detailed message
        if (data.error || data.risk_level === "Error") {
            const errorMsg = data.error || 'Unknown error occurred';
            const errorType = data.error_type || 'Error';
            showError(`${errorType}: ${errorMsg}`);
            throw new Error(errorMsg);
        }
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        return {
            clinical_probability: data.clinical_probability,
            retinal_probability: data.retinal_probability,
            fusion_probability: data.fused_probability,
            risk_category: data.risk_level
        };
    }
    
    // Display Results
    function displayResults(result) {
        const resultsHTML = `
            <h2>Prediction Results</h2>
            <p style="animation: fadeIn 0.5s ease-out 0.1s backwards;">
                <strong>Clinical Model Probability:</strong> ${(result.clinical_probability * 100).toFixed(1)}%
            </p>
            <p style="animation: fadeIn 0.5s ease-out 0.2s backwards;">
                <strong>Retinal Model Probability:</strong> ${(result.retinal_probability * 100).toFixed(1)}%
            </p>
            <p style="animation: fadeIn 0.5s ease-out 0.3s backwards;">
                <strong>Late Fusion Probability:</strong> ${(result.fusion_probability * 100).toFixed(1)}%
            </p>
            <h3 class="risk-category ${getRiskClass(result.risk_category)}" style="animation: fadeIn 0.5s ease-out 0.4s backwards;">
                Risk Category: ${result.risk_category}
            </h3>
        `;
        
        resultsCard.innerHTML = resultsHTML;
        
        // Add visual feedback
        resultsCard.style.border = `2px solid ${getRiskColor(result.risk_category)}`;
    }
    
    // Get risk category class
    function getRiskClass(category) {
        if (category === 'High Risk') return 'high-risk-result';
        if (category === 'Medium Risk') return 'medium-risk-result';
        return 'low-risk-result';
    }
    
    // Get risk category color
    function getRiskColor(category) {
        if (category === 'High Risk') return '#ff6b6b';
        if (category === 'Medium Risk') return '#ffb84d';
        return '#00d9a3';
    }
    
    // Show Error Message
    function showError(message) {
        // Create error notification
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-notification';
        errorDiv.innerHTML = `
            <span style="font-size: 20px;">⚠️</span>
            <span>${message}</span>
        `;
        
        document.body.appendChild(errorDiv);
        
        // Animate in
        setTimeout(() => errorDiv.classList.add('show'), 10);
        
        // Remove after 4 seconds
        setTimeout(() => {
            errorDiv.classList.remove('show');
            setTimeout(() => errorDiv.remove(), 300);
        }, 4000);
    }
    
    // Add input validation on blur
    ageInput.addEventListener('blur', function() {
        const age = parseFloat(this.value);
        if (this.value && (age < 18 || age > 120)) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
    
    bmiInput.addEventListener('blur', function() {
        const bmi = parseFloat(this.value);
        if (this.value && (bmi < 10 || bmi > 60)) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
    
    systolicBPInput.addEventListener('blur', function() {
        const systolic = parseFloat(this.value);
        if (this.value && (systolic < 70 || systolic > 250)) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
    
    diastolicBPInput.addEventListener('blur', function() {
        const diastolic = parseFloat(this.value);
        if (this.value && (diastolic < 40 || diastolic > 150)) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
    
    glucoseInput.addEventListener('blur', function() {
        const glucose = parseFloat(this.value);
        if (this.value && (glucose < 50 || glucose > 400)) {
            this.style.borderColor = '#ff6b6b';
        } else {
            this.style.borderColor = '';
        }
    });
});

// Add CSS animations and styles dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .spinner {
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        display: inline-block;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #ff6b6b, #ff8787);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(255, 107, 107, 0.3);
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transform: translateX(400px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .error-notification.show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .high-risk-result {
        color: #d63031 !important;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 107, 107, 0.05)) !important;
    }
    
    .medium-risk-result {
        color: #e17055 !important;
        background: linear-gradient(135deg, rgba(255, 184, 77, 0.1), rgba(255, 184, 77, 0.05)) !important;
    }
    
    .low-risk-result {
        color: #00b894 !important;
        background: linear-gradient(135deg, rgba(0, 217, 163, 0.1), rgba(0, 217, 163, 0.05)) !important;
    }
`;
document.head.appendChild(style);