// ========================================
// Language Toggle Functionality
// ========================================

// Translation data structure
const translations = {
    en: {
        // Will be populated with English text from data-en attributes
    },
    te: {
        // Will be populated with Telugu text from data-te attributes
    }
};

// Current language state
let currentLang = 'en';

// Initialize language toggle on page load
document.addEventListener('DOMContentLoaded', function() {
    initLanguageToggle();
    initImagePreview();
});

// ========================================
// Language Toggle System
// ========================================
function initLanguageToggle() {
    const btnEn = document.getElementById('lang-en');
    const btnTe = document.getElementById('lang-te');

    if (btnEn && btnTe) {
        btnEn.addEventListener('click', () => switchLanguage('en'));
        btnTe.addEventListener('click', () => switchLanguage('te'));
    }

    // Load saved language preference
    const savedLang = localStorage.getItem('preferred_language');
    if (savedLang) {
        switchLanguage(savedLang);
    }
}

function switchLanguage(lang) {
    currentLang = lang;
    
    // Update button states
    const btnEn = document.getElementById('lang-en');
    const btnTe = document.getElementById('lang-te');
    
    if (btnEn && btnTe) {
        btnEn.classList.toggle('active', lang === 'en');
        btnTe.classList.toggle('active', lang === 'te');
    }

    // Update all translatable elements
    const elements = document.querySelectorAll('[data-en][data-te]');
    elements.forEach(element => {
        const text = element.getAttribute(`data-${lang}`);
        if (text) {
            element.textContent = text;
        }
    });

    // Update placeholder text for inputs
    const inputs = document.querySelectorAll('input[data-placeholder-en][data-placeholder-te]');
    inputs.forEach(input => {
        const placeholder = input.getAttribute(`data-placeholder-${lang}`);
        if (placeholder) {
            input.placeholder = placeholder;
        }
    });

    // Save preference
    localStorage.setItem('preferred_language', lang);
}

// ========================================
// Image Preview Functionality
// ========================================
function initImagePreview() {
    const imageInput = document.getElementById('crop-image');
    const preview = document.getElementById('image-preview');
    const previewImg = document.getElementById('preview-img');

    if (imageInput && preview && previewImg) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if (file) {
                // Check file type
                if (!file.type.startsWith('image/')) {
                    alert('Please upload an image file');
                    return;
                }

                // Check file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Image size should be less than 5MB');
                    return;
                }

                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewImg.src = e.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }
}

// ========================================
// Form Validation (for future use)
// ========================================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('error');
            isValid = false;
        } else {
            field.classList.remove('error');
        }
    });

    return isValid;
}

// ========================================
// Utility Functions
// ========================================

// Format date to DD/MM/YYYY
function formatDate(date) {
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

// Calculate days between dates
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    return Math.round(Math.abs((firstDate - secondDate) / oneDay));
}

// Format currency (Indian Rupees)
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(amount);
}

// Show loading spinner
function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="spinner"></div>';
    }
}

// Hide loading spinner
function hideLoading(element, content) {
    if (element) {
        element.innerHTML = content;
    }
}

// Export functions for use in other scripts
window.forecastApp = {
    switchLanguage,
    validateForm,
    formatDate,
    daysBetween,
    formatCurrency,
    showLoading,
    hideLoading
};
