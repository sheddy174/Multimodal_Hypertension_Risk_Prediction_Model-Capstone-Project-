let breakdownCharts = {};
let predictionData = null;
let breakdownData = null;

document.addEventListener('DOMContentLoaded', async () => {
    const rawData = sessionStorage.getItem('hypertensionPrediction');
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');

    if (!rawData) {
        loading.innerHTML = '<p style="color: #ff6b6b;">No prediction data found. Please run a prediction first.</p>';
        return;
    }

    try {
        predictionData = JSON.parse(rawData);
    } catch (error) {
        loading.innerHTML = '<p style="color: #ff6b6b;">Unable to parse prediction data. Please try again.</p>';
        return;
    }

    try {
        const apiBase = window.APP_CONFIG?.API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${apiBase}/breakdown`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                clinical_data: predictionData.clinical_data,
                clinical_probability: predictionData.clinical_probability,
                retinal_probability: predictionData.retinal_probability,
                fusion_probability: predictionData.fusion_probability
            })
        });

        if (!response.ok) {
            throw new Error(`API returned ${response.status}`);
        }

        breakdownData = await response.json();
        loading.style.display = 'none';
        content.style.display = 'block';
        renderBreakdown(breakdownData);

    } catch (error) {
        console.error('Breakdown API error:', error);
        loading.innerHTML = `<p style="color: #ff6b6b;">Error loading breakdown: ${error.message}</p>`;
    }

    // PDF Export Handler
    document.getElementById('export-pdf')?.addEventListener('click', exportToPDF);
});

function renderBreakdown(data) {
    // 1. Risk Overview
    document.getElementById('risk-category').textContent = data.risk_category;
    document.getElementById('risk-percentage').textContent = (data.overall_risk * 100).toFixed(1) + '%';
    
    // Risk gauge chart
    renderRiskGauge(data.overall_risk, data.risk_category);
    
    // 2. Factor Contributions
    renderFactorsList(data.factor_contributions);
    renderContributionsChart(data.factor_contributions);
    
    // 3. Modifiable vs Non-Modifiable
    renderModifiableFactors(data.modifiable_factors);
    renderNonModifiableFactors(data.non_modifiable_factors);
    
    // 4. Recommendations
    renderRecommendations(data.top_recommendations);
    
    // 5. Potential Reduction
    const reduction = data.potential_risk_reduction;
    document.getElementById('reduction-amount').textContent = reduction.total + '%';
    document.getElementById('reduction-timeframe').textContent = reduction.timeframe;
    
    // 6. Ranges Comparison
    renderRangesComparison(predictionData.clinical_data);
    
    // 7. Model Scores
    document.getElementById('clinical-score').textContent = (data.model_breakdown.clinical * 100).toFixed(1) + '%';
    document.getElementById('retinal-score').textContent = (data.model_breakdown.retinal * 100).toFixed(1) + '%';
    document.getElementById('fusion-score').textContent = (data.model_breakdown.fusion * 100).toFixed(1) + '%';
}

function renderRiskGauge(risk, category) {
    const ctx = document.getElementById('risk-gauge-chart')?.getContext('2d');
    if (!ctx) return;
    
    const gaugeData = {
        labels: ['Your Risk', 'Remaining'],
        datasets: [{
            data: [risk * 100, (1 - risk) * 100],
            backgroundColor: [
                risk > 0.6 ? '#ff6b6b' : risk > 0.3 ? '#ffb84d' : '#00d9a3',
                '#f0f0f0'
            ],
            borderWidth: 0
        }]
    };
    
    if (breakdownCharts.gauge) breakdownCharts.gauge.destroy();
    breakdownCharts.gauge = new Chart(ctx, {
        type: 'doughnut',
        data: gaugeData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderContributionsChart(factors) {
    const ctx = document.getElementById('contributions-chart')?.getContext('2d');
    if (!ctx) return;
    
    const sortedFactors = Object.entries(factors)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    if (breakdownCharts.contributions) breakdownCharts.contributions.destroy();
    breakdownCharts.contributions = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sortedFactors.map(f => f[0].replace(/_/g, ' ').toUpperCase()),
            datasets: [{
                label: 'Contribution %',
                data: sortedFactors.map(f => f[1]),
                backgroundColor: '#088395',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, max: 100 }
            }
        }
    });
}

function renderFactorsList(factors) {
    const list = document.getElementById('factors-list');
    const items = Object.entries(factors).sort((a, b) => b[1] - a[1]);
    
    list.innerHTML = items.map(([name, contribution]) => `
        <div class="factor-item">
            <div class="factor-info">
                <div class="factor-name">${name.replace(/_/g, ' ')}</div>
                <div class="factor-value">Contributing to overall risk</div>
            </div>
            <div class="factor-contribution">${contribution.toFixed(1)}%</div>
        </div>
    `).join('');
}

function renderModifiableFactors(factors) {
    const list = document.getElementById('modifiable-list');
    list.innerHTML = factors.map(f => `
        <div class="factor-tag">
            <strong>${f.name}</strong><br>
            <small>Current: ${f.info.current} | Healthy: ${f.info.healthy}</small>
        </div>
    `).join('');
}

function renderNonModifiableFactors(factors) {
    const list = document.getElementById('non-modifiable-list');
    list.innerHTML = factors.map(f => `
        <div class="factor-tag">
            <strong>${f.name}</strong><br>
            <small>${f.info.current}</small>
        </div>
    `).join('');
}

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    container.innerHTML = recommendations.map((rec, idx) => `
        <div class="recommendation-card">
            <div class="recommendation-header">
                <div class="recommendation-title">Priority ${idx + 1}: ${rec.factor}</div>
                <span class="impact-badge impact-${rec.impact.toLowerCase()}">${rec.impact} Impact</span>
            </div>
            <div class="recommendation-actions">
                <ul>
                    ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                </ul>
            </div>
            <div class="expected-reduction">💡 Potential reduction: ${rec.expected_reduction}%</div>
        </div>
    `).join('');
}

function renderRangesComparison(clinicalData) {
    const container = document.getElementById('ranges-comparison');
    const ranges = [
        { label: 'Systolic BP', value: clinicalData.systolic_bp, min: 90, max: 180, unit: 'mmHg', healthy: 120 },
        { label: 'Diastolic BP', value: clinicalData.diastolic_bp, min: 60, max: 120, unit: 'mmHg', healthy: 80 },
        { label: 'Glucose', value: clinicalData.glucose, min: 70, max: 300, unit: 'mg/dL', healthy: 100 },
        { label: 'BMI', value: clinicalData.bmi, min: 15, max: 40, unit: '', healthy: 22 },
        { label: 'Cholesterol', value: clinicalData.totChol, min: 100, max: 400, unit: 'mg/dL', healthy: 200 },
        { label: 'Heart Rate', value: clinicalData.heartRate, min: 40, max: 120, unit: 'bpm', healthy: 70 }
    ];
    
    container.innerHTML = ranges.map(r => {
        const percentage = ((r.value - r.min) / (r.max - r.min)) * 100;
        const status = r.value > r.healthy ? '⚠️' : '✓';
        return `
            <div class="range-item">
                <div class="range-label">${r.label}</div>
                <div class="range-bar">
                    <div class="range-fill" style="width: ${Math.min(100, Math.max(0, percentage))}%;"></div>
                </div>
                <div class="range-status">${status}</div>
            </div>
        `;
    }).join('');
}

function exportToPDF() {
    if (!window.jspdf) {
        alert('PDF library not loaded');
        return;
    }
    
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF();
    pdf.text('HyperRNet - Hypertension Risk Analysis Report', 20, 20);
    pdf.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
    pdf.text(`Risk Level: ${breakdownData.risk_category}`, 20, 40);
    pdf.text(`Overall Risk: ${(breakdownData.overall_risk * 100).toFixed(1)}%`, 20, 50);
    pdf.save('hypertension_risk_report.pdf');
}
