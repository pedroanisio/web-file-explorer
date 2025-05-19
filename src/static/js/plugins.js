/**
 * Enhanced plugin system for the file explorer
 */

// Global functions for the Code Dump plugin
window.copyCodeDump = function() {
    const codeContent = document.getElementById('code-dump-content').textContent;
    const copyStatus = document.getElementById('copy-status');
    const copyBtn = document.getElementById('copy-button');
    const originalText = copyBtn.innerHTML;
    
    // Copy the text using the Clipboard API if available
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(codeContent)
            .then(() => {
                copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Copied!';
                if (copyStatus) {
                    copyStatus.textContent = 'Code copied to clipboard';
                    copyStatus.className = 'copy-status success';
                }
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
        copyBtn.innerHTML = originalText;
        if (copyStatus) {
            setTimeout(() => {
                copyStatus.textContent = '';
            }, 2000);
        }
    }, 2000);
};

window.fallbackCopyToClipboard = function(text) {
    // Create a temporary textarea to copy from
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed'; // Prevent scrolling to bottom
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        const copyStatus = document.getElementById('copy-status');
        const copyBtn = document.getElementById('copy-button');
        
        if (successful) {
            copyBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Copied!';
            if (copyStatus) {
                copyStatus.textContent = 'Code copied to clipboard';
                copyStatus.className = 'copy-status success';
            }
        } else {
            if (copyStatus) {
                copyStatus.textContent = 'Unable to copy code';
                copyStatus.className = 'copy-status error';
            }
        }
    } catch (err) {
        console.error('Failed to copy: ', err);
        if (document.getElementById('copy-status')) {
            document.getElementById('copy-status').textContent = 'Copy failed: ' + err;
            document.getElementById('copy-status').className = 'copy-status error';
        }
    }
    
    document.body.removeChild(textarea);
};

// Function to copy text to clipboard with visual feedback
function copyToClipboard(text, button) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text)
            .then(() => {
                button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Copied!';
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
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg> Copied!';
        } else {
            button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg> Failed';
        }
    } catch (err) {
        console.error('Failed to copy: ', err);
        button.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg> Failed';
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
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 4px;
            transition: background-color 0.2s;
        }
        .theme-dark .copy-button {
            background-color: #38a169;
        }
        .copy-button:hover {
            background-color: #45a049;
        }
        .theme-dark .copy-button:hover {
            background-color: #2f855a;
        }
        .copy-status {
            position: absolute;
            top: 10px;
            left: 10px;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }
        .copy-status.success {
            background-color: #d4edda;
            color: #155724;
        }
        .theme-dark .copy-status.success {
            background-color: #1c4532;
            color: #9ae6b4;
        }
        .copy-status.error {
            background-color: #f8d7da;
            color: #721c24;
        }
        .theme-dark .copy-status.error {
            background-color: #742a2a;
            color: #feb2b2;
        }
        .modal-content.with-copy-button {
            padding-top: 40px;
        }
        .modal-content.html-content {
            padding: 0;
        }
        .loading-animation {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #3498db;
            animation: spin 1s ease-in-out infinite;
        }
        .theme-dark .loading-animation {
            border-color: rgba(45, 55, 72, 0.3);
            border-top-color: #4299e1;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
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
            
            // Position the menu near the cursor
            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.classList.remove('hidden');
            
            // Add active class to the row
            this.classList.add('bg-gray-100');
            if (document.documentElement.classList.contains('theme-dark')) {
                this.classList.add('bg-gray-700');
            }
        });
    });

    document.addEventListener('click', function(e) {
        if (!contextMenu.contains(e.target)) {
            contextMenu.classList.add('hidden');
            // Remove active class from all rows
            document.querySelectorAll('tr.file-row').forEach(row => {
                row.classList.remove('bg-gray-100', 'bg-gray-700');
            });
        }
    });

    contextMenu.addEventListener('click', function(e) {
        const action = e.target.closest('li')?.getAttribute('data-action');
        if (!action) return;

        if (action === 'open') {
            window.open(`/preview/${encodeURIComponent(contextFilePath)}`, '_blank');
        } else if (action === 'download') {
            window.open(`/explore/${encodeURIComponent(contextFilePath)}`, '_blank');
        } else if (action === 'copy') {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(contextFilePath)
                    .then(() => {
                        showToast('Path copied to clipboard');
                    })
                    .catch(err => {
                        console.error('Failed to copy: ', err);
                        fallbackCopyPathToClipboard(contextFilePath);
                    });
            } else {
                fallbackCopyPathToClipboard(contextFilePath);
            }
        }

        contextMenu.classList.add('hidden');
        // Remove active class from all rows
        document.querySelectorAll('tr.file-row').forEach(row => {
            row.classList.remove('bg-gray-100', 'bg-gray-700');
        });
    });
    
    function fallbackCopyPathToClipboard(text) {
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showToast('Path copied to clipboard');
            } else {
                showToast('Failed to copy path', true);
            }
        } catch (err) {
            console.error('Failed to copy: ', err);
            showToast('Failed to copy path: ' + err, true);
        }
        
        document.body.removeChild(textarea);
    }
    
    function showToast(message, isError = false) {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.position = 'fixed';
            toastContainer.style.bottom = '20px';
            toastContainer.style.right = '20px';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `py-2 px-4 rounded shadow-lg mb-3 transition-all duration-300 transform translate-x-full ${isError ? 'bg-red-500 text-white' : 'bg-green-500 text-white'}`;
        toast.textContent = message;
        toastContainer.appendChild(toast);
        
        // Animate toast in
        setTimeout(() => {
            toast.style.transform = 'translateX(0)';
        }, 10);
        
        // Remove toast after delay
        setTimeout(() => {
            toast.style.transform = 'translateX(full)';
            toast.style.opacity = '0';
            setTimeout(() => {
                toastContainer.removeChild(toast);
                // If no more toasts, remove container
                if (toastContainer.children.length === 0) {
                    document.body.removeChild(toastContainer);
                }
            }, 300);
        }, 3000);
    }
    
    // Initialize the modal manager with references to DOM elements
    window.modalManager = {
        initialized: true,
        getElements: function() {
            return {
                modal: document.getElementById('modal'),
                modalTitle: document.getElementById('modal-title'),
                modalContent: document.getElementById('modal-content'),
                modalOverlay: document.getElementById('modal-overlay'),
                modalCloseButton: document.getElementById('modal-close')
            };
        }
    };
    
    // Define global showModal function
    window.showModalGlobal = function(title, content, isError = false, isHtml = false) {
        const elements = window.modalManager.getElements();
        
        if (!elements.modalOverlay || !elements.modal || !elements.modalTitle || !elements.modalContent) {
            console.error('Modal elements not found. Cannot display modal.');
            return;
        }
        
        elements.modalTitle.textContent = title;
        
        if (isError) {
            elements.modalContent.innerHTML = `<div class="error-message">${content}</div>`;
            elements.modalContent.classList.add('with-copy-button');
            elements.modalContent.classList.remove('html-content');
            
            let copyButton = elements.modalContent.parentNode.querySelector('.modal-copy-button');
            if (!copyButton) {
                copyButton = document.createElement('button');
                copyButton.textContent = 'Copy';
                copyButton.className = 'modal-copy-button copy-button';
                elements.modalContent.parentNode.appendChild(copyButton);
            }
        } else if (isHtml) {
            elements.modalContent.innerHTML = content;
            elements.modalContent.classList.remove('with-copy-button');
            elements.modalContent.classList.add('html-content');
            
            let copyButton = elements.modalContent.parentNode.querySelector('.modal-copy-button');
            if (copyButton) {
                copyButton.remove();
            }
        } else {
            elements.modalContent.textContent = content;
            elements.modalContent.classList.add('with-copy-button');
            elements.modalContent.classList.remove('html-content');
            
            let copyButton = elements.modalContent.parentNode.querySelector('.modal-copy-button');
            if (!copyButton) {
                copyButton = document.createElement('button');
                copyButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor"><path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" /><path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" /></svg>Copy';
                copyButton.className = 'modal-copy-button copy-button';
                elements.modalContent.parentNode.appendChild(copyButton);
            }
        }
        
        document.body.classList.add('modal-open'); // Prevent background scrolling
        elements.modalOverlay.style.display = 'flex'; // Show the overlay
        
        // Add active class after a small delay to trigger transition
        setTimeout(() => {
            elements.modalOverlay.classList.add('active');
        }, 10);
        
        // Resize any plotly charts after modal is shown
        setTimeout(() => {
            if (window.Plotly && isHtml) {
                const plots = document.querySelectorAll('.js-plotly-plot');
                plots.forEach(plot => {
                    window.Plotly.Plots.resize(plot);
                });
            }
        }, 300);
    };
    
    // Close modal when clicking close button or outside the modal
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            modalOverlay.classList.remove('active');
            setTimeout(() => {
                modalOverlay.style.display = 'none';
                document.body.classList.remove('modal-open');
            }, 300);
        });
    }
    
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                modalOverlay.classList.remove('active');
                setTimeout(() => {
                    modalOverlay.style.display = 'none';
                    document.body.classList.remove('modal-open');
                }, 300);
            }
        });
    }
    
    // Handle plugin toolbar items with loading indicator
    const toolbarItems = document.querySelectorAll('.toolbar-item');
    
    toolbarItems.forEach(item => {
        item.addEventListener('click', async function(e) {
            e.preventDefault(); // Prevent default action
            
            const pluginId = this.getAttribute('data-plugin-id');
            const currentPath = this.getAttribute('data-current-path');
            
            if (pluginId && currentPath) {
                // Disable the button during execution
                this.classList.add('opacity-50', 'cursor-not-allowed');
                const originalText = this.innerHTML;
                this.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Processing...`;
                
                try {
                    await executePlugin(pluginId, currentPath);
                } catch (error) {
                    console.error("Error executing plugin:", error);
                    showToast("Failed to execute plugin: " + error.message, true);
                } finally {
                    // Re-enable the button
                    this.classList.remove('opacity-50', 'cursor-not-allowed');
                    this.innerHTML = originalText;
                }
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
        if (selectedCount) {
            selectedCount.textContent = count;
        }
    }

    if (selectToggle && selectionActions) {
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
                showToast('No files selected', true);
                return;
            }
            
            // Show loading state
            downloadSelectedBtn.classList.add('opacity-50', 'cursor-not-allowed');
            const originalText = downloadSelectedBtn.innerHTML;
            downloadSelectedBtn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Creating zip...`;
            
            fetch('/download-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths })
            })
                .then(resp => {
                    if (!resp.ok) {
                        throw new Error('Download failed: ' + resp.statusText);
                    }
                    return resp.blob();
                })
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'selected_files.zip';
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    window.URL.revokeObjectURL(url);
                    showToast('Download started!');
                })
                .catch(err => {
                    console.error('Download failed', err);
                    showToast('Download failed: ' + err.message, true);
                })
                .finally(() => {
                    // Restore button state
                    downloadSelectedBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                    downloadSelectedBtn.innerHTML = originalText;
                });
        });
    }

    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('select-checkbox')) {
            updateSelectedCount();
        }
    });
    
    // When window is resized, fix the modal position and size
    window.addEventListener('resize', function() {
        if (modalOverlay && modalOverlay.style.display === 'flex') {
            const windowHeight = window.innerHeight;
            const windowWidth = window.innerWidth;
            
            // Adjust modal width on smaller screens
            if (windowWidth < 768) {
                modal.style.width = '95%';
                modal.style.maxWidth = '95%';
            } else {
                modal.style.width = 'auto';
                modal.style.maxWidth = '1200px';
            }
            
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

/**
 * Execute a plugin for a specific path
 * 
 * @param {string} pluginId - The ID of the plugin to execute
 * @param {string} path - The path to process
 */
async function executePlugin(pluginId, path) {
    // Show loading modal while processing
    window.showModalGlobal('Processing...', `
        <div class="flex justify-center items-center p-8">
            <div class="loading-animation"></div>
            <div class="ml-4 text-lg text-gray-600 dark:text-gray-300">
                Running ${pluginId.replace(/_/g, ' ')}...
            </div>
        </div>
    `, false, true);
    
    try {
        const response = await fetch(`/plugins/execute/${pluginId}?path=${encodeURIComponent(path)}`);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Server responded with ${response.status}: ${response.statusText}. Details: ${errorText}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            const isHtml = (data.content_type && data.content_type.toLowerCase() === 'text/html') || data.is_html === true;
            window.showModalGlobal(data.title || pluginId, data.output, false, isHtml);
        } else {
            window.showModalGlobal('Error', data.error || 'Unknown error occurred while executing plugin.', true);
        }
    } catch (error) {
        console.error('Error executing plugin:', error);
        window.showModalGlobal('Client-Side Error', `Failed to execute plugin: ${error.message}`, true);
    }
}