// HyperRNet - Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Animate statistics on page load
    animateStats();
    
    // Add interactivity to charts
    initializeCharts();
    
    // Handle filter changes
    setupFilters();
    
    // Setup table interactions
    setupTableInteractions();
});

// Animate statistics counters
function animateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    
    statNumbers.forEach(stat => {
        const target = stat.textContent;
        
        // Check if it's a number or percentage
        if (target.includes('%')) {
            animatePercentage(stat, target);
        } else if (target.includes(',')) {
            animateNumber(stat, target);
        }
    });
}

function animateNumber(element, target) {
    const cleanTarget = parseInt(target.replace(/,/g, ''));
    const duration = 1500;
    const start = 0;
    const increment = cleanTarget / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= cleanTarget) {
            element.textContent = cleanTarget.toLocaleString();
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current).toLocaleString();
        }
    }, 16);
}

function animatePercentage(element, target) {
    const cleanTarget = parseFloat(target.replace('%', ''));
    const duration = 1500;
    const start = 0;
    const increment = cleanTarget / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= cleanTarget) {
            element.textContent = cleanTarget + '%';
            clearInterval(timer);
        } else {
            element.textContent = current.toFixed(1) + '%';
        }
    }, 16);
}

// Initialize chart interactions
function initializeCharts() {
    // Add hover effects to bar chart
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        bar.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 8px 16px rgba(0, 0, 0, 0.2)';
        });
        
        bar.addEventListener('mouseleave', function() {
            this.style.boxShadow = 'none';
        });
    });
    
    // Animate metric fills
    animateMetricBars();
}

function animateMetricBars() {
    const metricFills = document.querySelectorAll('.metric-fill');
    
    metricFills.forEach((fill, index) => {
        const targetWidth = fill.style.width;
        fill.style.width = '0%';
        
        setTimeout(() => {
            fill.style.width = targetWidth;
        }, 500 + (index * 200));
    });
}

// Setup filter functionality
function setupFilters() {
    const chartFilter = document.querySelector('.chart-filter');
    
    if (chartFilter) {
        chartFilter.addEventListener('change', function() {
            // Show loading state
            showLoadingOverlay();
            
            // Simulate data refresh
            setTimeout(() => {
                hideLoadingOverlay();
                // In production, fetch new data based on selected period
                console.log('Filter changed to:', this.value);
            }, 800);
        });
    }
}

// Setup table interactions
function setupTableInteractions() {
    const tableButtons = document.querySelectorAll('.btn-table');
    
    tableButtons.forEach(button => {
        button.addEventListener('click', function() {
            const row = this.closest('tr');
            const patientId = row.cells[0].textContent;
            viewPatientDetails(patientId);
        });
    });
    
    // Add hover effect to table rows
    const tableRows = document.querySelectorAll('.predictions-table tbody tr');
    tableRows.forEach(row => {
        row.style.cursor = 'pointer';
        
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking the button
            if (!e.target.classList.contains('btn-table')) {
                const patientId = this.cells[0].textContent;
                highlightRow(this);
            }
        });
    });
}

// View patient details
function viewPatientDetails(patientId) {
    // Show modal or navigate to details page
    showNotification(`Viewing details for ${patientId}`, 'info');
    
    // In production, this would navigate to a details page or open a modal
    // window.location.href = `patient-details.html?id=${patientId}`;
}

// Highlight selected row
function highlightRow(row) {
    // Remove highlight from other rows
    const allRows = document.querySelectorAll('.predictions-table tbody tr');
    allRows.forEach(r => r.style.backgroundColor = '');
    
    // Highlight selected row
    row.style.backgroundColor = 'rgba(5, 191, 219, 0.08)';
}

// Show loading overlay
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="loading-spinner"></div>
        <p>Updating data...</p>
    `;
    document.body.appendChild(overlay);
    
    setTimeout(() => overlay.classList.add('show'), 10);
}

// Hide loading overlay
function hideLoadingOverlay() {
    const overlay = document.querySelector('.loading-overlay');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => overlay.remove(), 300);
    }
}

// Show notification
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: '✅',
        info: 'ℹ️',
        warning: '⚠️',
        error: '❌'
    };
    
    notification.innerHTML = `
        <span class="notification-icon">${icons[type]}</span>
        <span class="notification-message">${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Refresh dashboard data
function refreshDashboard() {
    showLoadingOverlay();
    
    // Simulate API call
    setTimeout(() => {
        // Re-animate stats
        animateStats();
        animateMetricBars();
        
        hideLoadingOverlay();
        showNotification('Dashboard data refreshed', 'success');
    }, 1500);
}

// Add dynamic styles
const style = document.createElement('style');
style.textContent = `
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(15, 28, 46, 0.8);
        backdrop-filter: blur(4px);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .loading-overlay.show {
        opacity: 1;
    }
    
    .loading-overlay p {
        color: white;
        margin-top: 20px;
        font-size: 16px;
        font-weight: 500;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(5, 191, 219, 0.3);
        border-top-color: #05bfdb;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transform: translateX(400px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .notification.show {
        opacity: 1;
        transform: translateX(0);
    }
    
    .notification-success {
        background: linear-gradient(135deg, #00d9a3, #00b894);
        color: white;
    }
    
    .notification-info {
        background: linear-gradient(135deg, #05bfdb, #088395);
        color: white;
    }
    
    .notification-warning {
        background: linear-gradient(135deg, #ffb84d, #ffa502);
        color: white;
    }
    
    .notification-error {
        background: linear-gradient(135deg, #ff6b6b, #ff8787);
        color: white;
    }
    
    .notification-icon {
        font-size: 20px;
    }
    
    .stat-card {
        cursor: pointer;
    }
    
    .predictions-table tbody tr {
        transition: all 0.2s ease;
    }
`;
document.head.appendChild(style);