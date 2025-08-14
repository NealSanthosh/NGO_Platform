// Admin panel specific JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Organization verification functionality
    const verifyButtons = document.querySelectorAll('.verify-org-btn');
    verifyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orgId = this.dataset.orgId;
            const action = this.dataset.action;
            const orgName = this.dataset.orgName;
            
            showVerificationModal(orgId, action, orgName);
        });
    });
    
    // Show verification modal
    function showVerificationModal(orgId, action, orgName) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${action.charAt(0).toUpperCase() + action.slice(1)} Organization</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p>Are you sure you want to <strong>${action}</strong> "${orgName}"?</p>
                        <div class="mb-3">
                            <label for="admin-notes" class="form-label">Admin Notes (Optional)</label>
                            <textarea class="form-control" id="admin-notes" rows="3" placeholder="Add any notes..."></textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-${action === 'approve' ? 'success' : 'danger'}" onclick="processVerification('${orgId}', '${action}')">
                            ${action.charAt(0).toUpperCase() + action.slice(1)}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Clean up modal after hide
        modal.addEventListener('hidden.bs.modal', function() {
            document.body.removeChild(modal);
        });
    }
    
    // Process organization verification
    window.processVerification = function(orgId, action) {
        const notes = document.getElementById('admin-notes').value;
        
        fetch(`/admin/verify-organisation/${orgId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: action,
                notes: notes
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Hide modal
                const modal = bootstrap.Modal.getInstance(document.querySelector('.modal.show'));
                modal.hide();
                
                // Show success message
                DonationPlatform.showNotification(data.message, 'success');
                
                // Refresh page after short delay
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                DonationPlatform.showNotification(data.message, 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            DonationPlatform.showNotification('An error occurred. Please try again.', 'danger');
        });
    };
    
    // Database management
    const dbActions = document.querySelectorAll('.db-action-btn');
    dbActions.forEach(button => {
        button.addEventListener('click', function() {
            const action = this.dataset.action;
            const collection = this.dataset.collection;
            
            if (confirm(`Are you sure you want to ${action} the ${collection} collection?`)) {
                performDbAction(action, collection, this);
            }
        });
    });
    
    function performDbAction(action, collection, button) {
        const originalText = button.textContent;
        button.textContent = 'Processing...';
        button.disabled = true;
        
        // Simulate database action (replace with actual API call)
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
            DonationPlatform.showNotification(`${action} completed for ${collection}`, 'success');
        }, 2000);
    }
    
    // Financial reports chart initialization
    if (document.getElementById('monthlyDonationsChart')) {
        initializeFinancialCharts();
    }
    
    function initializeFinancialCharts() {
        // Monthly donations chart
        const ctx = document.getElementById('monthlyDonationsChart').getContext('2d');
        
        // Sample data - replace with actual data from backend
        const monthlyData = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Monthly Donations ($)',
                data: [12000, 19000, 8000, 25000, 22000, 30000],
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderColor: 'rgba(0, 123, 255, 1)',
                borderWidth: 2,
                fill: true
            }]
        };
        
        new Chart(ctx, {
            type: 'line',
            data: monthlyData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Real-time updates for dashboard stats
    if (document.querySelector('.admin-dashboard')) {
        setInterval(updateDashboardStats, 30000); // Update every 30 seconds
    }
    
    function updateDashboardStats() {
        fetch('/admin/api/stats')
            .then(response => response.json())
            .then(data => {
                // Update stat cards
                document.querySelector('#total-users .stat-number').textContent = data.total_users;
                document.querySelector('#total-orgs .stat-number').textContent = data.total_orgs;
                document.querySelector('#total-campaigns .stat-number').textContent = data.total_campaigns;
                document.querySelector('#pending-verifications .stat-number').textContent = data.pending_verifications;
            })
            .catch(error => {
                console.error('Error updating stats:', error);
            });
    }
    
    // Export functionality
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const format = this.dataset.format;
            const type = this.dataset.type;
            
            exportData(format, type, this);
        });
    });
    
    function exportData(format, type, button) {
        const originalText = button.textContent;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Exporting...';
        button.disabled = true;
        
        // Create download link
        const downloadUrl = `/admin/export/${type}?format=${format}`;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${type}_export_${new Date().toISOString().split('T')[0]}.${format}`;
        link.click();
        
        // Reset button
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
            DonationPlatform.showNotification(`${type} data exported successfully`, 'success');
        }, 2000);
    }
    
    // Search functionality for admin tables
    const searchInputs = document.querySelectorAll('.admin-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table tbody');
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? 'table-row' : 'none';
            });
        });
    });
    
    // Bulk actions
    const selectAllCheckboxes = document.querySelectorAll('.select-all');
    selectAllCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const table = this.closest('table');
            const itemCheckboxes = table.querySelectorAll('.item-checkbox');
            
            itemCheckboxes.forEach(itemCheckbox => {
                itemCheckbox.checked = this.checked;
            });
            
            updateBulkActions();
        });
    });
    
    // Individual item checkboxes
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActions);
    });
    
    function updateBulkActions() {
        const checkedBoxes = document.querySelectorAll('.item-checkbox:checked');
        const bulkActions = document.querySelector('.bulk-actions');
        
        if (bulkActions) {
            if (checkedBoxes.length > 0) {
                bulkActions.classList.remove('d-none');
                bulkActions.querySelector('.selected-count').textContent = checkedBoxes.length;
            } else {
                bulkActions.classList.add('d-none');
            }
        }
    }
});
