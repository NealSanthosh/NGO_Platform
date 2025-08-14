// Main JavaScript functionality
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

    // Auto-hide alerts
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);

    // Form validation
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

    // Image preview functionality
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            const previewContainer = document.querySelector(`#${input.id}-preview`);
            
            if (file && previewContainer) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    previewContainer.innerHTML = `<img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">`;
                };
                reader.readAsDataURL(file);
            }
        });
    });

    // Donation amount buttons
    const donationButtons = document.querySelectorAll('.donation-amount-btn');
    donationButtons.forEach(button => {
        button.addEventListener('click', function() {
            const amount = this.dataset.amount;
            const amountInput = document.querySelector('#donation-amount');
            if (amountInput) {
                amountInput.value = amount;
                donationButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const progressObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.style.width;
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = width;
                }, 100);
            }
        });
    }, observerOptions);

    progressBars.forEach(bar => {
        progressObserver.observe(bar);
    });

    // Search functionality
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const searchResults = document.querySelector('.search-results');
            const items = document.querySelectorAll('.searchable-item');

            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });

    // Loading states for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.closest('form').addEventListener('submit', function() {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
        });
    });

    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.target;
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                navigator.clipboard.writeText(targetElement.textContent).then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                });
            }
        });
    });

    // Dynamic content loading
    const loadMoreButtons = document.querySelectorAll('.load-more-btn');
    loadMoreButtons.forEach(button => {
        button.addEventListener('click', function() {
            const container = document.querySelector(this.dataset.container);
            const url = this.dataset.url;
            const page = parseInt(this.dataset.page) + 1;

            fetch(`${url}?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    if (data.items && data.items.length > 0) {
                        container.insertAdjacentHTML('beforeend', data.html);
                        this.dataset.page = page;
                        
                        if (!data.has_next) {
                            this.style.display = 'none';
                        }
                    } else {
                        this.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error loading more content:', error);
                });
        });
    });
});

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(dateString));
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Export functions for use in other scripts
window.DonationPlatform = {
    formatCurrency,
    formatDate,
    showNotification
};
