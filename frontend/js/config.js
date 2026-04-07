// Configuration for API endpoints
// This file makes it easy to switch between development and production

const CONFIG = {
    // Automatically detect environment
    API_BASE_URL: (() => {
        const hostname = window.location.hostname;

        // Development (local)
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://127.0.0.1:8000';
        }

        // Production (Render backend)
        // TODO: Replace with your actual Render backend URL after deployment
        return 'https://hyperrnet.onrender.com';
    })(),

    // Other config settings
    MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5MB
    ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/jpg', 'image/png'],
    SESSION_TIMEOUT: 30 * 60 * 1000 // 30 minutes
};

// Make config available globally
window.APP_CONFIG = CONFIG;

console.log('🔧 Environment:', CONFIG.API_BASE_URL.includes('localhost') ? 'Development' : 'Production');
console.log('🌐 API Base URL:', CONFIG.API_BASE_URL);