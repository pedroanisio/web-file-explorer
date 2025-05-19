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

// Function to copy text to clipboard
function copyToClipboard(text, button) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text)
            .then(() => {
                button.textContent = '✅ Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy: ', err);
                fallbackCopyTextToClipboard(text, button);
            });
    } else {
        fallbackCopyTextToClipboard(text, button);
    }
}

// Fallback copy method for browsers that don't support clipboard API
function fallbackCopyTextToClipboard(text, button) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            button.textContent = '✅ Copied!';
        } else {
            button.textContent = '❌ Failed';
        }
    } catch (err) {
        console.error('Failed to copy: ', err);
        button.textContent = '❌ Failed';
    }
    
    document.body.removeChild(textarea);
    setTimeout(() => {
        button.textContent = 'Copy';
    }, 2000);
}

document.addEventListener('DOMContentLoaded', function() {
    // Set up modal
    const modal = document.getElementById('modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    const modalOverlay = document.getElementById('modal-overlay');
    const closeModal = document.querySelector('.modal-close');
    
    // Add CSS for the copy button and improved modal
    const style = document.createElement('style');
    style.textContent = `
        .copy-button {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
        }
        .copy-button:hover {
            background: #45a049;
        }
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
            width: 92%;
            max-width: 1400px;
            max-height: 92vh;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            background-color: #f8f9fa;
            border-radius: 8px 8px 0 0;
            z-index: 10;
        }
        .modal-title {
            margin: 0;
            font-size: 1.5rem;
            color: #2c3e50;
            font-weight: 600;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #7f8c8d;
            transition: color 0.2s;
        }
        .modal-close:hover {
            color: #333;
        }
        .modal-body {
            flex: 1;
            overflow: auto;
            padding: 0;
        }
        .modal-content {
            position: relative;
            padding: 15px;
            background-color: #f8f9fa;
            overflow-x: auto;
            white-space: pre-wrap;
            height: 100%;
            margin: 0;
            border-radius: 0 0 8px 8px;
        }
        .modal-content.with-copy-button {
            padding-top: 40px;
        }
        .error-message {
            color: #e74c3c;
            font-family: monospace;
            white-space: pre-wrap;
            padding: 15px;
        }
        /* Make plotly charts responsive in the modal */
        .modal-body .js-plotly-plot {
            width: 100%;
            height: 100%;
        }
        /* Remove padding when showing HTML content like Git analyzer */
        .modal-content.html-content {
            padding: 0;
        }
        /* Adjust iframe styles if needed for embedded content */
        .modal-content iframe {
            width: 100%;
            border: none;
        }
    `;
    document.head.appendChild(style);
    
    // Set up click event delegation for the copy button
    document.addEventListener('click', function(event) {
        if (event.target && event.target.id === 'copy-button') {
            window.copyCodeDump();
        } else if (event.target && event.target.classList.contains('modal-copy-button')) {
            const textToCopy = event.target.closest('.modal-body').querySelector('.modal-content').innerText;
            copyToClipboard(textToCopy, event.target);
        }
    });

    // Context menu for file actions
    const contextMenu = document.getElementById('file-context-menu');
    let contextFilePath = null;

    document.querySelectorAll('tr.file-row').forEach(row => {
        row.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            contextFilePath = this.getAttribute('data-file-path');
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.classList.remove('hidden');
        });
    });

    document.addEventListener('click', function(e) {
        if (!contextMenu.contains(e.target)) {
            contextMenu.classList.add('hidden');
        }
    });

    contextMenu.addEventListener('click', function(e) {
        const action = e.target.getAttribute('data-action');
        if (!action) return;

        if (action === 'open') {
            window.open(`/preview/${encodeURIComponent(contextFilePath)}`, '_blank');
        } else if (action === 'download') {
            window.open(`/explore/${encodeURIComponent(contextFilePath)}`, '_blank');
        } else if (action === 'copy') {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(contextFilePath);
            } else {
                const textarea = document.createElement('textarea');
                textarea.value = contextFilePath;
                textarea.style.position = 'fixed';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                } finally {
                    document.body.removeChild(textarea);
                }
            }
        }

        contextMenu.classList.add('hidden');
    });
    
    // Use the global showModal function for this scope
    const showModal = showModalGlobal;
    
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
            
            if (pluginId && currentPath) {
                executePlugin(pluginId, currentPath);
            }
        });
    });

    // Multi-select functionality
    const selectToggle = document.getElementById('select-toggle');
    const selectionActions = document.getElementById('selection-actions');
    const selectAllBtn = document.getElementById('select-all');
    const deselectAllBtn = document.getElementById('deselect-all');
    const downloadSelectedBtn = document.getElementById('download-selected');
    const selectedCount = document.getElementById('selected-count');

    function getCheckboxes() {
        return Array.from(document.querySelectorAll('.select-checkbox'));
    }

    function updateSelectedCount() {
        const count = getCheckboxes().filter(cb => cb.checked).length;
        selectedCount.textContent = count;
    }

    if (selectToggle) {
        selectToggle.addEventListener('click', () => {
            const active = selectionActions.classList.toggle('hidden') === false;
            document.querySelectorAll('.select-column').forEach(col => {
                if (active) {
                    col.classList.remove('hidden');
                } else {
                    col.classList.add('hidden');
                    const input = col.querySelector('input[type="checkbox"]');
                    if (input) input.checked = false;
                }
            });
            selectToggle.textContent = active ? 'Cancel' : 'Select';
            updateSelectedCount();
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = true);
            updateSelectedCount();
        });
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = false);
            updateSelectedCount();
        });
    }

    if (downloadSelectedBtn) {
        downloadSelectedBtn.addEventListener('click', () => {
            const paths = getCheckboxes().filter(cb => cb.checked).map(cb => cb.dataset.path);
            if (!paths.length) {
                return;
            }
            fetch('/download-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths })
            })
                .then(resp => resp.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'selected_files.zip';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                })
                .catch(err => console.error('Download failed', err));
        });
    }

    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('select-checkbox')) {
            updateSelectedCount();
        }
    });
    
    // When window is resized, fix the modal position and size
    window.addEventListener('resize', function() {
        if (modalOverlay.style.display === 'flex') {
            const windowHeight = window.innerHeight;
            const modalHeight = windowHeight * 0.92;
            modal.style.height = `${modalHeight}px`;
            
            const headerHeight = modal.querySelector('.modal-header').offsetHeight;
            modal.querySelector('.modal-body').style.height = `${modalHeight - headerHeight}px`;
            
            // Resize any plotly charts
            if (window.Plotly) {
                const plots = document.querySelectorAll('.js-plotly-plot');
                plots.forEach(plot => {
                    window.Plotly.Plots.resize(plot);
                });
            }
        }
    });
});

// Define showModal globally so it can be used by executePlugin
let showModalGlobal;

// Define showModalGlobal before using it
window.showModalGlobal = function(title, content, isError = false, isHtml = false) {
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    const modalOverlay = document.getElementById('modal-overlay');
    const modal = document.getElementById('modal');
    
    if (!modalTitle || !modalContent || !modalOverlay || !modal) {
        console.error('Modal elements not found. DOM might not be fully loaded.');
        return;
    }
    
    modalTitle.textContent = title;
    
    if (isError) {
        modalContent.innerHTML = `<div class="error-message">${content}</div>`;
        modalContent.classList.add('with-copy-button');
        modalContent.classList.remove('html-content');
        
        // Add copy button for errors
        let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
        if (!copyButton) {
            copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.className = 'modal-copy-button copy-button';
            modalContent.parentNode.appendChild(copyButton);
        }
    } else if (isHtml) {
        modalContent.innerHTML = content;
        modalContent.classList.remove('with-copy-button');
        modalContent.classList.add('html-content');
        
        // Remove any existing copy button for HTML content
        let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
        if (copyButton) {
            copyButton.remove();
        }
    } else {
        modalContent.textContent = content;
        modalContent.classList.add('with-copy-button');
        modalContent.classList.remove('html-content');
        
        // Add copy button for plain text
        let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
        if (!copyButton) {
            copyButton = document.createElement('button');
            copyButton.textContent = 'Copy';
            copyButton.className = 'modal-copy-button copy-button';
            modalContent.parentNode.appendChild(copyButton);
        }
    }
    
    modalOverlay.style.display = 'flex';
    
    // Apply any necessary height adjustments for better display
    const windowHeight = window.innerHeight;
    const modalHeight = windowHeight * 0.92;
    modal.style.height = `${modalHeight}px`;
    
    // Dynamically adjust modal-body height based on header
    const headerHeight = modal.querySelector('.modal-header').offsetHeight;
    modal.querySelector('.modal-body').style.height = `${modalHeight - headerHeight}px`;
    
    // Initialize any charts that might be in the modal
    setTimeout(() => {
        if (window.Plotly && isHtml) {
            const plots = document.querySelectorAll('.js-plotly-plot');
            plots.forEach(plot => {
                window.Plotly.Plots.resize(plot);
            });
        }
    }, 100);
};

document.addEventListener('DOMContentLoaded', function() {
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('modal-content');
        const modalOverlay = document.getElementById('modal-overlay');
        
        modalTitle.textContent = title;
        
        if (isError) {
            modalContent.innerHTML = `<div class="error-message">${content}</div>`;
            modalContent.classList.add('with-copy-button');
            modalContent.classList.remove('html-content');
            
            // Add copy button for errors
            let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
            if (!copyButton) {
                copyButton = document.createElement('button');
                copyButton.textContent = 'Copy';
                copyButton.className = 'modal-copy-button copy-button';
                modalContent.parentNode.appendChild(copyButton);
            }
        } else if (isHtml) {
            modalContent.innerHTML = content;
            modalContent.classList.remove('with-copy-button');
            modalContent.classList.add('html-content');
            
            // Remove any existing copy button for HTML content
            let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
            if (copyButton) {
                copyButton.remove();
            }
        } else {
            modalContent.textContent = content;
            modalContent.classList.add('with-copy-button');
            modalContent.classList.remove('html-content');
            
            // Add copy button for plain text
            let copyButton = modalContent.parentNode.querySelector('.modal-copy-button');
            if (!copyButton) {
                copyButton = document.createElement('button');
                copyButton.textContent = 'Copy';
                copyButton.className = 'modal-copy-button copy-button';
                modalContent.parentNode.appendChild(copyButton);
            }
        }
        
        modalOverlay.style.display = 'flex';
        
        // Apply any necessary height adjustments for better display
        const windowHeight = window.innerHeight;
        const modalHeight = windowHeight * 0.92;
        const modal = document.getElementById('modal');
        modal.style.height = `${modalHeight}px`;
        
        // Dynamically adjust modal-body height based on header
        const headerHeight = modal.querySelector('.modal-header').offsetHeight;
        modal.querySelector('.modal-body').style.height = `${modalHeight - headerHeight}px`;
        
        // Initialize any charts that might be in the modal
        setTimeout(() => {
            if (window.Plotly && isHtml) {
                const plots = document.querySelectorAll('.js-plotly-plot');
                plots.forEach(plot => {
                    window.Plotly.Plots.resize(plot);
                });
            }
        }, 100);
    };
});

/**
 * Execute a plugin for a specific path
 * 
 * @param {string} pluginId - The ID of the plugin to execute
 * @param {string} path - The path to process
 */
async function executePlugin(pluginId, path) {
    try {
        // Show loading indicator in modal
        showModalGlobal('Processing...', '<div class="flex justify-center items-center p-8"><div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div></div>', true);
        
        // Fetch plugin result using the existing endpoint format
        const response = await fetch(`/plugins/execute/${pluginId}?path=${encodeURIComponent(path)}`);
        
        if (!response.ok) {
            throw new Error(`Server responded with ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Check if the result is HTML content
            const isHtml = (data.content_type && data.content_type === 'html') || data.is_html === true;
            
            // Update the modal with the plugin output
            showModalGlobal(data.title || pluginId, data.output, isHtml);
        } else {
            // Show error in modal
            showModalGlobal('Error', data.error || 'Unknown error occurred', false);
        }
    } catch (error) {
        console.error('Error executing plugin:', error);
        showModalGlobal('Error', `Failed to execute plugin: ${error.message}`, false);
    }
}
