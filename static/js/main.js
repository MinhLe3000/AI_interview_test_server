// Main JavaScript for Interview AI System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Show file info
                const fileName = file.name;
                const fileSize = (file.size / 1024 / 1024).toFixed(2);
                
                // Create or update file info display
                let fileInfo = input.parentNode.querySelector('.file-info');
                if (!fileInfo) {
                    fileInfo = document.createElement('div');
                    fileInfo.className = 'file-info mt-2';
                    input.parentNode.appendChild(fileInfo);
                }
                
                fileInfo.innerHTML = `
                    <small class="text-success">
                        <i class="fas fa-check-circle me-1"></i>
                        ${fileName} (${fileSize} MB)
                    </small>
                `;
            }
        });
    });

    // Loading state management
    window.showLoading = function(element, text = 'Đang xử lý...') {
        const originalContent = element.innerHTML;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            ${text}
        `;
        element.disabled = true;
        return originalContent;
    };

    window.hideLoading = function(element, originalContent) {
        element.innerHTML = originalContent;
        element.disabled = false;
    };

    // Copy to clipboard functionality
    window.copyToClipboard = function(text, button) {
        navigator.clipboard.writeText(text).then(() => {
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Đã sao chép';
            button.classList.add('btn-success');
            button.classList.remove('btn-outline-secondary');
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.classList.remove('btn-success');
                button.classList.add('btn-outline-secondary');
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    };

    // Progress bar animation
    window.animateProgress = function(progressBar, targetValue, duration = 1000) {
        const startValue = 0;
        const increment = targetValue / (duration / 16);
        let currentValue = startValue;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            progressBar.style.width = currentValue + '%';
        }, 16);
    };

    // Confirmation dialogs
    window.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };

    // Auto-save functionality for forms
    const autoSaveForms = document.querySelectorAll('[data-autosave]');
    autoSaveForms.forEach(form => {
        const formData = {};
        
        // Load saved data
        const savedData = localStorage.getItem(`autosave_${form.dataset.autosave}`);
        if (savedData) {
            try {
                const parsed = JSON.parse(savedData);
                Object.keys(parsed).forEach(key => {
                    const element = form.querySelector(`[name="${key}"]`);
                    if (element) {
                        element.value = parsed[key];
                    }
                });
            } catch (e) {
                console.error('Error loading autosave data:', e);
            }
        }
        
        // Save on input
        form.addEventListener('input', function(e) {
            if (e.target.name) {
                formData[e.target.name] = e.target.value;
                localStorage.setItem(`autosave_${form.dataset.autosave}`, JSON.stringify(formData));
            }
        });
        
        // Clear on submit
        form.addEventListener('submit', function() {
            localStorage.removeItem(`autosave_${form.dataset.autosave}`);
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement && activeElement.form) {
                e.preventDefault();
                activeElement.form.submit();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('.modal.show');
            openModals.forEach(modal => {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) {
                    bsModal.hide();
                }
            });
        }
    });

    // Lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });

    cards.forEach(card => cardObserver.observe(card));

    // Print functionality
    window.printPage = function() {
        window.print();
    };

    // Theme toggle (if implemented)
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('darkTheme', document.body.classList.contains('dark-theme'));
        });

        // Load saved theme
        if (localStorage.getItem('darkTheme') === 'true') {
            document.body.classList.add('dark-theme');
        }
    }
});

// Utility functions
const Utils = {
    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Format date
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Export for use in other scripts
window.InterviewAI = {
    Utils: Utils,
    showLoading: window.showLoading,
    hideLoading: window.hideLoading,
    copyToClipboard: window.copyToClipboard,
    animateProgress: window.animateProgress,
    confirmAction: window.confirmAction,
    printPage: window.printPage
};
