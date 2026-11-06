/**
 * Student Management System - Frontend JavaScript Helpers
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const wrapper = document.getElementById('wrapper');

    if (sidebarToggle && wrapper) {
        sidebarToggle.addEventListener('click', function (e) {
            e.preventDefault();
            wrapper.classList.toggle('toggled');
        });
    }

    // 2. Auto-dismiss Flash Alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Check if bootstrap alert instance exists, then close it
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });
});

/**
 * Helper function to configure delete confirmation modals dynamically
 * @param {string} entityName - Name of the entity being deleted (e.g. 'Student Alex')
 * @param {string} actionUrl - URL to submit the POST deletion request to
 */
function confirmDelete(entityName, actionUrl) {
    const modalEl = document.getElementById('deleteConfirmModal');
    if (!modalEl) return;

    const entityNameTarget = document.getElementById('deleteEntityName');
    const deleteForm = document.getElementById('deleteForm');

    if (entityNameTarget) {
        entityNameTarget.textContent = entityName;
    }
    if (deleteForm) {
        deleteForm.action = actionUrl;
    }

    const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
    modal.show();
}

