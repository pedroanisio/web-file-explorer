/**
 * Plugin system for the file explorer
 */

// Global functions for the Code Dump plugin
window.copyCodeDump = function() {
    const codeContent = document.getElementById('code-dump-content').textContent;
    const copyStatus = document.getElementById('copy-status');
    const copyBtn = document.getElementById('copy-button');
    const originalText = copyBtn.textContent;
    
    // First try using the modern Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(codeContent)
            .then(() => {
                copyBtn.textContent = '✅ Copied!';
                copyStatus.textContent = 'All code copied to clipboard';
                copyStatus.className = 'copy-status success';
            })
            .catch(err => {
                console.error('Failed to copy: ', err);
                // Fall back to the older method
                window.fallbackCopyToClipboard(codeContent);
            });
    } else {
        // Fall back to the older method for browsers that don't support clipboard API
        window.fallbackCopyToClipboard(codeContent);
    }
    
    // Revert button text after a delay
    setTimeout(() => {
        copyBtn.textContent = originalText;
        setTimeout(() => {
            copyStatus.textContent = '';
        }, 2000);
    }, 2000);
};

window.fallbackCopyToClipboard = function(text) {
    // Create a temporary textarea to copy from
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed'; // Prevent scrolling to bottom
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        const copyStatus = document.getElementById('copy-status');
        const copyBtn = document.getElementById('copy-button');
        
        if (successful) {
            copyBtn.textContent = '✅ Copied!';
            copyStatus.textContent = 'All code copied to clipboard';
            copyStatus.className = 'copy-status success';
        } else {
            copyStatus.textContent = 'Unable to copy code';
            copyStatus.className = 'copy-status error';
        }
    } catch (err) {
        console.error('Failed to copy: ', err);
        document.getElementById('copy-status').textContent = 'Copy failed: ' + err;
        document.getElementById('copy-status').className = 'copy-status error';
    }
    
    document.body.removeChild(textarea);
};

document.addEventListener('DOMContentLoaded', function() {
    // Set up modal
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    const modalOverlay = document.getElementById('modal-overlay');
    const closeModal = document.querySelector('.modal-close');
    
    // Set up click event delegation for the copy button
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'copy-button') {
            window.copyCodeDump();
        }
    });
    
    // Function to show modal with content
    function showModal(title, content, isError = false, isHtml = false) {
        modalTitle.textContent = title;
        
        if (isError) {
            modalContent.innerHTML = `<div class="error-message">${content}</div>`;
        } else if (isHtml) {
            modalContent.innerHTML = content;
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
                        showModal(data.title || 'Plugin Result', data.output, false, data.is_html);
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
