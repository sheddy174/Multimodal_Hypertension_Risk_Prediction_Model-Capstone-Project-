document.addEventListener('DOMContentLoaded', async () => {
    const rawData = sessionStorage.getItem('hypertensionRiskBreakdown');
    const contributionList = document.getElementById('contribution-list');
    const summaryContent = document.getElementById('summary-content');

    if (!rawData) {
        summaryContent.innerHTML = '<p>No prediction data found. Please run a prediction first.</p>';
        return;
    }

    let data;
    try {
        data = JSON.parse(rawData);
    } catch (error) {
        summaryContent.innerHTML = '<p>Unable to parse breakdown data. Please try again.</p>';
        return;
    }

    try {
        const response = await fetch(`${window.APP_CONFIG.API_BASE_URL}/breakdown`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                clinical_data: data.clinical_data,
                clinical_probability: data.clinical_probability,
                retinal_probability: data.retinal_probability,
                fusion_probability: data.fusion_probability,
                risk_level: data.risk_category
            })
        });

        const breakdownData = await response.json();

        if (!response.ok) {
            throw new Error(breakdownData.error || 'Failed to load risk breakdown');
        }

        renderSummary(breakdownData.summary);
        renderContributions(breakdownData.contributions);

    } catch (error) {
        console.error('Breakdown API error:', error);
        summaryContent.innerHTML = `
            <div class="summary-item">
                <h3>Final Risk Category</h3>
                <p>${data.risk_category}</p>
            </div>
            <div class="summary-item">
                <h3>Predicted Fusion Risk</h3>
                <p>${(data.fusion_probability * 100).toFixed(1)}%</p>
            </div>
            <div class="summary-item">
                <h3>Retinal Model Score</h3>
                <p>${(data.retinal_probability * 100).toFixed(1)}%</p>
            </div>
            <div class="summary-item">
                <h3>Clinical Model Score</h3>
                <p>${(data.clinical_probability * 100).toFixed(1)}%</p>
            </div>
        `;

        const contributions = buildContributions(data);
        const topContributors = contributions.sort((a, b) => b.score - a.score);
        contributionList.innerHTML = topContributors.map(item => renderContributionCard(item)).join('');
    }
});

function renderSummary(summary) {
    const summaryContent = document.getElementById('summary-content');
    summaryContent.innerHTML = `
        <div class="summary-item">
            <h3>Final Risk Category</h3>
            <p>${summary.risk_category}</p>
        </div>
        <div class="summary-item">
            <h3>Predicted Fusion Risk</h3>
            <p>${(summary.fusion_probability * 100).toFixed(1)}%</p>
        </div>
        <div class="summary-item">
            <h3>Retinal Model Score</h3>
            <p>${(summary.retinal_probability * 100).toFixed(1)}%</p>
        </div>
        <div class="summary-item">
            <h3>Clinical Model Score</h3>
            <p>${(summary.clinical_probability * 100).toFixed(1)}%</p>
        </div>
    `;
}

function renderContributions(contributions) {
    const contributionList = document.getElementById('contribution-list');
    contributionList.innerHTML = contributions
        .sort((a, b) => b.score - a.score)
        .map(item => renderContributionCard(item))
        .join('');
}

function buildContributions(data) {
    const d = data.clinical_data;
    const age = Number(d.age || 0);
    const bmi = Number(d.bmi || 22);
    const systolic = Number(d.systolic_bp || 120);
    const diastolic = Number(d.diastolic_bp || 80);
    const glucose = Number(d.glucose || 100);
    const cholesterol = Number(d.totChol || 200);
    const smoking = Number(d.currentSmoker || 0);
    const diabetes = Number(d.diabetes || 0);
    const bpMeds = Number(d.BPMeds || 0);
    const heartRate = Number(d.heartRate || 75);

    return [
        {
            title: 'Systolic Blood Pressure',
            score: normalize((systolic - 110) / 80),
            detail: `Higher systolic pressure is a strong hypertension driver. Current reading: ${systolic} mmHg.`
        },
        {
            title: 'Diastolic Blood Pressure',
            score: normalize((diastolic - 70) / 80),
            detail: `Diastolic pressure influences long-term vascular risk. Current reading: ${diastolic} mmHg.`
        },
        {
            title: 'Age',
            score: normalize((age - 35) / 45),
            detail: `Hypertension risk generally increases with age. Current age: ${age}.`
        },
        {
            title: 'BMI',
            score: normalize((bmi - 22) / 18),
            detail: `Higher BMI is associated with greater cardiovascular strain. Current BMI: ${bmi}.`
        },
        {
            title: 'Glucose',
            score: normalize((glucose - 90) / 120),
            detail: `Elevated glucose can contribute to metabolic risk. Current level: ${glucose} mg/dL.`
        },
        {
            title: 'Cholesterol',
            score: normalize((cholesterol - 180) / 120),
            detail: `High cholesterol can worsen vascular health. Current level: ${cholesterol} mg/dL.`
        },
        {
            title: 'Smoking Status',
            score: smoking === 1 ? 1 : 0.05,
            detail: `${smoking === 1 ? 'Smoking increases cardiovascular strain.' : 'Non-smoker status lowers risk.'}`
        },
        {
            title: 'Diabetes',
            score: diabetes === 1 ? 1 : 0.05,
            detail: `${diabetes === 1 ? 'Diabetes raises hypertension risk.' : 'No diabetes lowers risk.'}`
        },
        {
            title: 'Blood Pressure Medication',
            score: bpMeds === 1 ? 0.95 : 0.25,
            detail: `${bpMeds === 1 ? 'Medication indicates existing hypertension treatment.' : 'No BP medications suggests lower treatment dependency.'}`
        },
        {
            title: 'Heart Rate',
            score: normalize((heartRate - 60) / 60),
            detail: `Higher resting heart rate is often linked with elevated risk. Current rate: ${heartRate} bpm.`
        },
        {
            title: 'Retinal Model Contribution',
            score: clamp(data.retinal_probability),
            detail: 'The fundus image model indicates how strongly retinal changes support hypertension risk.'
        },
        {
            title: 'Fusion Impact',
            score: clamp(data.fusion_probability),
            detail: 'The final prediction combines both clinical and retinal evidence.'
        }
    ];
}

function renderContributionCard(item) {
    const score = Math.round(item.score * 100);
    return `
        <div class="contribution-card">
            <strong>${item.title}</strong>
            <span class="score-pill">${score}%</span>
            <div class="bar-track">
                <div class="bar-fill" style="width: ${score}%;"></div>
            </div>
            <p>${item.detail}</p>
        </div>
    `;
}

function normalize(value) {
    return clamp(value, 0, 1);
}

function clamp(value, min = 0, max = 1) {
    return Math.min(Math.max(value, min), max);
}
