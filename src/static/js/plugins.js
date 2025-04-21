/**
 * Plugin system for the file explorer
 */
document.addEventListener('DOMContentLoaded', function() {
    // Set up modal
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    const modalOverlay = document.getElementById('modal-overlay');
    const closeModal = document.querySelector('.modal-close');
    
    // Function to show modal with content
    function showModal(title, content, isError = false) {
        modalTitle.textContent = title;
        
        if (isError) {
            modalContent.innerHTML = `<div class="error-message">${content}</div>`;
        } else {
            modalContent.textContent = content;
        }
        
        modalOverlay.style.display = 'flex';
    }
    
    // Close modal when clicking close button or outside the modal
    closeModal.addEventListener('click', function() {
        modalOverlay.style.display = 'none';
    });
    
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) {
            modalOverlay.style.display = 'none';
        }
    });
    
    // Handle plugin toolbar items
    const toolbarItems = document.querySelectorAll('.toolbar-item');
    
    toolbarItems.forEach(item => {
        item.addEventListener('click', function() {
            const pluginId = this.getAttribute('data-plugin-id');
            const currentPath = this.getAttribute('data-current-path');
            
            // Show loading state
            showModal('Loading...', 'Executing plugin, please wait...');
            
            // Make AJAX request to execute plugin
            fetch(`/plugins/execute/${pluginId}?path=${encodeURIComponent(currentPath)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showModal(data.title || 'Plugin Result', data.output);
                    } else {
                        showModal('Error', data.error + '\n\n' + (data.output || ''), true);
                    }
                })
                .catch(error => {
                    showModal('Error', 'Failed to execute plugin: ' + error.message, true);
                });
        });
    });
});
