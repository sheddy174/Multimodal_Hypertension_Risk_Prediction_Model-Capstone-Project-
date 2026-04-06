// HyperRNet - History Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Get DOM elements
    const searchInput = document.querySelector('.search-input');
    const riskFilter = document.querySelectorAll('.filter-select')[0];
    const dateFilter = document.querySelectorAll('.filter-select')[1];
    const tableBody = document.querySelector('.predictions-table tbody');
    const recordCount = document.querySelector('.record-count');
    const pageButtons = document.querySelectorAll('.page-num');
    const prevButton = document.querySelector('.page-btn:first-of-type');
    const nextButton = document.querySelector('.page-btn:last-of-type');
    
    // Store all predictions data
    let allPredictions = [];
    let filteredPredictions = [];
    let currentPage = 1;
    const recordsPerPage = 10;
    
    // Initialize
    initializeData();
    setupEventListeners();
    
    // Initialize data from table
    function initializeData() {
        const rows = tableBody.querySelectorAll('tr');
        allPredictions = Array.from(rows).map(row => ({
            element: row.cloneNode(true),
            id: row.cells[0].textContent,
            date: row.cells[1].textContent,
            age: row.cells[2].textContent,
            clinical: row.cells[3].textContent,
            retinal: row.cells[4].textContent,
            fusion: row.cells[5].textContent,
            risk: row.cells[6].querySelector('.badge').textContent
        }));
        
        filteredPredictions = [...allPredictions];
    }
    
    // Setup event listeners
    function setupEventListeners() {
        // Search input
        searchInput.addEventListener('input', debounce(handleSearch, 300));
        
        // Filters
        riskFilter.addEventListener('change', handleFilter);
        dateFilter.addEventListener('change', handleFilter);
        
        // Pagination
        pageButtons.forEach(button => {
            button.addEventListener('click', function() {
                changePage(parseInt(this.textContent));
            });
        });
        
        prevButton.addEventListener('click', () => changePage(currentPage - 1));
        nextButton.addEventListener('click', () => changePage(currentPage + 1));
        
        // Table row clicks
        setupTableInteractions();
        
        // Export button
        const exportBtn = document.querySelector('.btn-secondary');
        if (exportBtn) {
            exportBtn.addEventListener('click', exportToCSV);
        }
    }
    
    // Handle search
    function handleSearch() {
        const query = searchInput.value.toLowerCase().trim();
        
        if (!query) {
            filteredPredictions = [...allPredictions];
        } else {
            filteredPredictions = allPredictions.filter(pred => 
                pred.id.toLowerCase().includes(query) ||
                pred.date.toLowerCase().includes(query) ||
                pred.risk.toLowerCase().includes(query)
            );
        }
        
        applyFilters();
        currentPage = 1;
        renderTable();
    }
    
    // Handle filters
    function handleFilter() {
        applyFilters();
        currentPage = 1;
        renderTable();
    }
    
    // Apply all filters
    function applyFilters() {
        let results = [...allPredictions];
        
        // Apply search
        const query = searchInput.value.toLowerCase().trim();
        if (query) {
            results = results.filter(pred => 
                pred.id.toLowerCase().includes(query) ||
                pred.date.toLowerCase().includes(query) ||
                pred.risk.toLowerCase().includes(query)
            );
        }
        
        // Apply risk filter
        const riskValue = riskFilter.value;
        if (riskValue !== 'All Risk Levels') {
            results = results.filter(pred => pred.risk === riskValue);
        }
        
        // Apply date filter (simplified - in production, implement actual date filtering)
        const dateValue = dateFilter.value;
        // TODO: Implement date range filtering
        
        filteredPredictions = results;
    }
    
    // Render table
    function renderTable() {
        // Clear table
        tableBody.innerHTML = '';
        
        // Calculate pagination
        const startIndex = (currentPage - 1) * recordsPerPage;
        const endIndex = startIndex + recordsPerPage;
        const pageData = filteredPredictions.slice(startIndex, endIndex);
        
        // Render rows
        if (pageData.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" style="text-align: center; padding: 40px; color: #718096;">
                        No predictions found matching your criteria
                    </td>
                </tr>
            `;
        } else {
            pageData.forEach(pred => {
                const row = pred.element.cloneNode(true);
                tableBody.appendChild(row);
            });
        }
        
        // Update record count
        recordCount.textContent = `Showing ${filteredPredictions.length} records`;
        
        // Update pagination
        updatePagination();
        
        // Re-setup table interactions
        setupTableInteractions();
    }
    
    // Update pagination controls
    function updatePagination() {
        const totalPages = Math.ceil(filteredPredictions.length / recordsPerPage);
        
        // Update page buttons
        pageButtons.forEach((button, index) => {
            const pageNum = index + 1;
            button.textContent = pageNum;
            
            if (pageNum === currentPage) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
            
            if (pageNum > totalPages) {
                button.style.display = 'none';
            } else {
                button.style.display = 'block';
            }
        });
        
        // Update prev/next buttons
        prevButton.disabled = currentPage === 1;
        nextButton.disabled = currentPage >= totalPages;
    }
    
    // Change page
    function changePage(page) {
        const totalPages = Math.ceil(filteredPredictions.length / recordsPerPage);
        
        if (page < 1 || page > totalPages) return;
        
        currentPage = page;
        renderTable();
        
        // Scroll to top of table
        document.querySelector('.recent-predictions').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
    
    // Setup table interactions
    function setupTableInteractions() {
        const viewButtons = tableBody.querySelectorAll('.btn-table');
        const rows = tableBody.querySelectorAll('tr');
        
        viewButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                const row = this.closest('tr');
                const patientId = row.cells[0].textContent;
                viewPatientDetails(patientId);
            });
        });
        
        rows.forEach(row => {
            row.style.cursor = 'pointer';
            row.addEventListener('click', function() {
                highlightRow(this);
            });
        });
    }
    
    // View patient details
    function viewPatientDetails(patientId) {
        showNotification(`Loading details for ${patientId}...`, 'info');
        
        // Simulate loading
        setTimeout(() => {
            // In production, navigate to details page or show modal
            console.log('View details for:', patientId);
            showNotification(`Details loaded for ${patientId}`, 'success');
        }, 800);
    }
    
    // Highlight row
    function highlightRow(row) {
        const allRows = tableBody.querySelectorAll('tr');
        allRows.forEach(r => r.style.backgroundColor = '');
        row.style.backgroundColor = 'rgba(5, 191, 219, 0.08)';
    }
    
    // Export to CSV
    function exportToCSV() {
        showNotification('Preparing CSV export...', 'info');
        
        // Prepare CSV data
        const headers = ['Patient ID', 'Date & Time', 'Age', 'Clinical Score', 'Retinal Score', 'Fusion Score', 'Risk Level'];
        const rows = filteredPredictions.map(pred => [
            pred.id,
            pred.date,
            pred.age,
            pred.clinical,
            pred.retinal,
            pred.fusion,
            pred.risk
        ]);
        
        // Create CSV content
        let csvContent = headers.join(',') + '\n';
        rows.forEach(row => {
            csvContent += row.join(',') + '\n';
        });
        
        // Create download
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `hypertension_predictions_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showNotification('CSV exported successfully!', 'success');
    }
    
    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
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
});

// Add dynamic styles
const style = document.createElement('style');
style.textContent = `
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
`;
document.head.appendChild(style);