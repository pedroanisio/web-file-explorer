/**
 * Enhanced plugin system and common UI utilities for the file explorer
 */

// --- Start: Global Utilities (could be moved to a separate utils.js if project grows) ---

/**
 * Shows a toast notification.
 * @param {string} message - The message to display.
 * @param {string} type - Type of toast: 'success' (default), 'error', 'warning'.
 * @param {number} duration - How long the toast stays visible (in ms).
 */
window.showToast = function(message, type = 'success', duration = 3000) {
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        // Styling for toast-container is in components.css
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = 'toast-message'; // Base class
    let iconSvg = '';

    switch (type) {
        case 'error':
            toast.classList.add('toast-error');
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-10a1 1 0 011 1v2a1 1 0 11-2 0v-2a1 1 0 011-1zm0 4a1 1 0 100 2 1 1 0 000-2z" clip-rule="evenodd" /></svg>`;
            break;
        case 'warning':
            toast.classList.add('toast-warning');
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" /></svg>`; //
            break;
        case 'success':
        default:
            // Default to success, .toast-message already has success colors
            iconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>`; //
            break;
    }

    toast.innerHTML = `${iconSvg}<span>${message}</span>`;
    toastContainer.appendChild(toast);

    // Animate toast in
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
        toast.style.opacity = '1';
    }, 10);

    // Remove toast after delay
    setTimeout(() => {
        toast.style.transform = 'translateX(110%)'; // Slide out
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode === toastContainer) { // Check if still child
                toastContainer.removeChild(toast);
            }
            if (toastContainer.children.length === 0) {
                if (toastContainer.parentNode === document.body) { // Check if still child
                    document.body.removeChild(toastContainer);
                }
            }
        }, 300); // Wait for animation
    }, duration);
};


/**
 * Copies text to the clipboard.
 * @param {string} text - The text to copy.
 * @param {HTMLElement} [button] - Optional button element to give feedback on.
 * @param {string} [successMessage] - Optional message for the button on success.
 * @returns {Promise<void>}
 */
window.copyTextToClipboard = async function(text, button, successMessage = 'Copied!') {
    const originalButtonText = button ? button.innerHTML : '';
    const iconSuccess = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`;
    const iconError = `<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" /></svg>`;

    function setButtonFeedback(msg, icon = iconSuccess) {
        if (button) button.innerHTML = `${icon} ${msg}`;
    }

    function resetButtonText() {
        if (button) button.innerHTML = originalButtonText;
    }

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            setButtonFeedback(successMessage);
            showToast('Text copied to clipboard', 'success');
        } else {
            // Fallback for insecure contexts or older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed'; // Prevent scrolling to bottom
            textArea.style.opacity = '0';
            document.body.appendChild(textArea);
            textArea.select();
            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);
            if (successful) {
                setButtonFeedback(successMessage);
                showToast('Text copied to clipboard (fallback)', 'success');
            } else {
                throw new Error('Fallback copy command failed.');
            }
        }
    } catch (err) {
        console.error('Failed to copy text: ', err);
        setButtonFeedback('Failed', iconError);
        showToast('Failed to copy text.', 'error');
    } finally {
        if (button) {
            setTimeout(resetButtonText, 2000);
        }
    }
};

// --- End: Global Utilities ---


// --- Modal Management ---
window.modalManager = {
    modalOverlay: null,
    modal: null,
    modalTitle: null,
    modalContent: null,
    modalCloseButton: null,
    copyButton: null, // Reference to the modal's copy button

    init: function() {
        this.modalOverlay = document.getElementById('modal-overlay');
        this.modal = document.getElementById('modal');
        this.modalTitle = document.getElementById('modal-title');
        this.modalContent = document.getElementById('modal-content'); // This is the <pre> or <div> inside modal-body
        this.modalCloseButton = document.getElementById('modal-close');

        if (this.modalOverlay) {
            this.modalOverlay.addEventListener('click', (e) => {
                if (e.target === this.modalOverlay) this.hide();
            });
        }
        if (this.modalCloseButton) {
            this.modalCloseButton.addEventListener('click', () => this.hide());
        }
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modalOverlay && this.modalOverlay.classList.contains('active')) {
                this.hide();
            }
        });
    },

    show: function(title, content, { isError = false, isHtml = false, showCopyButton = false, copyText = '' } = {}) {
        if (!this.modalOverlay || !this.modal || !this.modalTitle || !this.modalContent) {
            console.error('Modal elements not found. Cannot display modal.');
            return;
        }

        this.modalTitle.textContent = title;
        this.modalContent.classList.remove('error-message', 'html-content', 'with-copy-button'); // Reset classes

        // Remove existing copy button if present
        if (this.copyButton && this.copyButton.parentNode) {
            this.copyButton.parentNode.removeChild(this.copyButton);
            this.copyButton = null;
        }

        if (isError) {
            this.modalContent.innerHTML = ''; // Clear previous content
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-message'; // Styled by tailwind-styles.css
            errorDiv.textContent = content;
            this.modalContent.appendChild(errorDiv);
        } else if (isHtml) {
            // Ensure HTML content is properly rendered
            console.log("Setting HTML content:", content.substring(0, 100) + "...");
            
            // Make sure div has proper styling for HTML content
            this.modalContent.classList.add('html-content');
            
            // Set the HTML content
            this.modalContent.innerHTML = content;
            
            // Add debugging to check if content was set properly
            console.log("Modal content after setting HTML:", 
                this.modalContent.childNodes.length + " child nodes");
        } else {
            this.modalContent.textContent = content; // Defaults to pre-wrap in CSS
        }

        if (showCopyButton && !isHtml) { // Typically don't show copy for raw HTML display
            this.modalContent.classList.add('with-copy-button'); // Adds padding if needed
            this.copyButton = document.createElement('button');
            this.copyButton.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor"><path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" /><path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" /></svg>Copy`; //
            this.copyButton.className = 'btn btn-blue btn-sm modal-copy-button'; // Use global button styles
            // The .modal-copy-button class can be used for specific positioning if needed by tailwind-styles.css

            const textToCopy = copyText || content;
            this.copyButton.addEventListener('click', () => window.copyTextToClipboard(textToCopy, this.copyButton));
            
            // Prepend to modal-body, or append to modal-header for different placement
            if(this.modalBody) { // Assuming modalBody is the direct parent of modalContent
                 this.modalBody.insertBefore(this.copyButton, this.modalContent); // Place before content
            } else {
                 this.modal.querySelector('.modal-header').appendChild(this.copyButton); // Fallback: header
            }
        }

        document.body.classList.add('modal-open'); //
        this.modalOverlay.style.display = 'flex'; //
        setTimeout(() => {
            this.modalOverlay.classList.add('active'); //
        }, 10);

        // Resize Plotly charts if any, after modal is fully visible
        setTimeout(() => {
            if (window.Plotly && isHtml) {
                const plots = this.modalContent.querySelectorAll('.js-plotly-plot');
                if (plots.length > 0) {
                    console.log(`Found ${plots.length} Plotly charts to resize`);
                    plots.forEach(plot => {
                        try {
                            window.Plotly.Plots.resize(plot);
                        } catch (error) {
                            console.error("Error resizing Plotly chart:", error);
                        }
                    });
                }
            }
        }, 350); // Ensure transition is complete
    },

    hide: function() {
        if (this.modalOverlay) {
            this.modalOverlay.classList.remove('active');
            setTimeout(() => {
                this.modalOverlay.style.display = 'none';
                document.body.classList.remove('modal-open');
                if (this.modalContent) this.modalContent.innerHTML = ''; // Clear content
                if (this.modalTitle) this.modalTitle.textContent = 'Modal Title'; // Reset title
            }, 300); // Match CSS transition duration
        }
    }
};
// --- End: Modal Management ---


document.addEventListener('DOMContentLoaded', function() {
    modalManager.init(); // Initialize modal manager
    modalManager.modalBody = document.getElementById('modal-body'); // Assign modalBody


    // Context menu for file actions
    const contextMenu = document.getElementById('file-context-menu');
    let contextFilePath = null;

    document.querySelectorAll('tr.file-row').forEach(row => {
        row.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            contextFilePath = this.getAttribute('data-file-path');
            if (!contextMenu || !contextFilePath) return;

            contextMenu.style.top = `${e.pageY}px`;
            contextMenu.style.left = `${e.pageX}px`;
            contextMenu.classList.remove('hidden');

            // Remove active class from other rows and add to this one
            document.querySelectorAll('tr.file-row.active-row').forEach(activeRow => activeRow.classList.remove('active-row', 'bg-gray-100', 'dark:bg-gray-700'));
            this.classList.add('active-row', 'bg-gray-100', 'dark:bg-gray-700'); //
        });
    });

    document.addEventListener('click', function(e) {
        if (contextMenu && !contextMenu.contains(e.target) && !e.target.closest('tr.file-row')) {
            contextMenu.classList.add('hidden');
            document.querySelectorAll('tr.file-row.active-row').forEach(row => row.classList.remove('active-row', 'bg-gray-100', 'dark:bg-gray-700'));
        }
    });

    if (contextMenu) {
        contextMenu.addEventListener('click', function(e) {
            const actionItem = e.target.closest('li');
            if (!actionItem) return;
            const action = actionItem.getAttribute('data-action');
            if (!action || !contextFilePath) return;

            if (action === 'open') { //
                // Assuming preview URL is needed, or adjust as per actual open action
                const previewUrl = `/preview/${encodeURIComponent(contextFilePath)}`;
                window.open(previewUrl, '_blank');
            } else if (action === 'download') { //
                 window.open(`/explore/${encodeURIComponent(contextFilePath)}`, '_self'); // Use _self to trigger browser download for the file
            } else if (action === 'copy') { //
                window.copyTextToClipboard(contextFilePath, actionItem.querySelector('button')); // Pass a button like element if available for feedback
            }

            contextMenu.classList.add('hidden');
            document.querySelectorAll('tr.file-row.active-row').forEach(row => row.classList.remove('active-row', 'bg-gray-100', 'dark:bg-gray-700'));
        });
    }

    // Handle plugin toolbar items with loading indicator
    const toolbarItems = document.querySelectorAll('.toolbar-item');
    toolbarItems.forEach(item => {
        item.addEventListener('click', async function(e) {
            e.preventDefault();
            if (this.classList.contains('disabled')) return;

            const pluginId = this.getAttribute('data-plugin-id');
            const currentPath = this.getAttribute('data-current-path');
            const supportsPage = this.getAttribute('data-supports-page') === 'true';
            const schemaVersion = this.getAttribute('data-schema-version');

            // Check if this is a V2 plugin with page mode support
            if (supportsPage && schemaVersion === '2.0') {
                // Show dropdown for V2 plugins with page support
                const wrapper = this.closest('.toolbar-item-wrapper');
                const dropdown = wrapper.querySelector('.toolbar-dropdown');
                if (dropdown) {
                    // Hide all other dropdowns first
                    document.querySelectorAll('.toolbar-dropdown').forEach(d => {
                        if (d !== dropdown) d.classList.add('hidden');
                    });
                    dropdown.classList.toggle('hidden');
                    e.stopPropagation();
                    return;
                }
            }

            // Standard execution for V1 plugins or V2 plugins without page mode
            if (pluginId && typeof currentPath !== 'undefined') { // currentPath can be empty string for root
                this.classList.add('disabled'); //
                const originalText = this.innerHTML;
                this.innerHTML = `<svg class="animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Processing...`; //

                try {
                    await executePlugin(pluginId, currentPath);
                } catch (error) {
                    console.error("Error executing plugin:", error);
                    window.showToast("Failed to execute plugin: " + error.message, 'error'); //
                } finally {
                    this.classList.remove('disabled');
                    this.innerHTML = originalText; //
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
    const selectedCountSpan = document.getElementById('selected-count'); //

    function getCheckboxes() {
        return Array.from(document.querySelectorAll('.select-checkbox')); //
    }

    function updateSelectedCount() {
        if (!selectedCountSpan) return;
        const count = getCheckboxes().filter(cb => cb.checked).length; //
        selectedCountSpan.textContent = count; //
        if (downloadSelectedBtn) {
            downloadSelectedBtn.disabled = count === 0;
            if (count === 0) {
                downloadSelectedBtn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                downloadSelectedBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }
    }

    if (selectToggle && selectionActions) {
        selectToggle.addEventListener('click', () => {
            const isSelectionActive = selectionActions.classList.toggle('hidden');
            const isActive = !isSelectionActive; // if hidden is false, it's active

            document.querySelectorAll('.select-column').forEach(col => {
                col.classList.toggle('hidden', !isActive); //
                if (!isActive) { // If cancelling selection
                    const input = col.querySelector('input[type="checkbox"]');
                    if (input) input.checked = false; //
                }
            });
            selectToggle.textContent = isActive ? 'Cancel Select' : 'Select Items'; //
            updateSelectedCount();
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = true);
            updateSelectedCount(); //
        });
    }

    if (deselectAllBtn) {
        deselectAllBtn.addEventListener('click', () => {
            getCheckboxes().forEach(cb => cb.checked = false);
            updateSelectedCount(); //
        });
    }

    if (downloadSelectedBtn) {
        downloadSelectedBtn.disabled = true; // Initially disable
        downloadSelectedBtn.classList.add('opacity-50', 'cursor-not-allowed');

        downloadSelectedBtn.addEventListener('click', () => {
            const paths = getCheckboxes().filter(cb => cb.checked).map(cb => cb.dataset.path);
            if (!paths.length) {
                window.showToast('No files selected', 'warning'); //
                return;
            }

            downloadSelectedBtn.classList.add('opacity-50', 'cursor-not-allowed'); //
            const originalBtnText = downloadSelectedBtn.innerHTML;
            downloadSelectedBtn.innerHTML = `<svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Creating zip...`; //

            fetch('/download-selected', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ paths }) //
            })
            .then(resp => {
                if (!resp.ok) { //
                    return resp.json().then(err => { throw new Error(err.error || 'Download failed: ' + resp.statusText); });
                }
                return resp.blob(); //
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'selected_files.zip'; //
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
                window.showToast('Download started!', 'success'); //
            })
            .catch(err => {
                console.error('Download failed', err);
                window.showToast(err.message, 'error'); //
            })
            .finally(() => {
                downloadSelectedBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                downloadSelectedBtn.innerHTML = originalBtnText; //
                updateSelectedCount(); // Re-evaluate disabled state
            });
        });
    }

    document.addEventListener('change', function(e) {
        if (e.target && e.target.classList.contains('select-checkbox')) {
            updateSelectedCount(); //
        }
    });

    // Window resize handler for modals (if specific adjustments are needed beyond CSS)
    window.addEventListener('resize', function() {
        if (modalManager.modalOverlay && modalManager.modalOverlay.style.display === 'flex') { //
            // Currently, CSS handles responsiveness. Add JS logic if needed.
            // Example: Adjust Plotly charts inside a modal
            if (window.Plotly) {
                const plots = modalManager.modalContent.querySelectorAll('.js-plotly-plot');
                plots.forEach(plot => window.Plotly.Plots.resize(plot)); //
            }
        }
    });
});

/**
 * Execute a plugin for a specific path
 * @param {string} pluginId - The ID of the plugin to execute
 * @param {string} path - The path to process
 */
async function executePlugin(pluginId, path) {
    const loadingModalContent = `
        <div class="loading-modal">
            <div class="loading-animation"></div>
            <div class="ml-4 text-lg text-gray-700 dark:text-gray-300">
                Running ${pluginId.replace(/_/g, ' ')}...
            </div>
        </div>`; //
    
    // Show a non-blocking loading indicator or a simplified modal
    // For this example, we'll use the main modal but make it clear it's loading
    modalManager.show('Processing...', loadingModalContent, { isHtml: true }); //

    try {
        const response = await fetch(`/plugins/execute/${pluginId}?path=${encodeURIComponent(path)}`); //
        if (!response.ok) {
            const errorText = await response.text(); //
            throw new Error(`Server responded with ${response.status}: ${response.statusText}. Details: ${errorText}`);
        }

        const data = await response.json(); //
        if (data.success) {
            // Check if this is a download response
            if (data.download) {
                // Hide the loading modal
                modalManager.hide();
                
                // Create a temporary anchor to trigger the download
                const a = document.createElement('a');
                a.href = `/download-plugin-file?file_path=${encodeURIComponent(data.download.file_path)}&filename=${encodeURIComponent(data.download.filename)}`;
                a.download = data.download.filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                
                // Show success message
                window.showToast(data.message || 'Download started!', 'success');
            } else {
                // Fix for HTML content type - ensure content is properly marked as HTML
                const isHtml = data.content_type === "html" || 
                               (data.content_type && data.content_type.toLowerCase() === 'text/html') || 
                               data.is_html === true;
                
                // For debugging
                console.log("Plugin response:", {
                    pluginId,
                    contentType: data.content_type,
                    isHtml: isHtml,
                    outputLength: data.output ? data.output.length : 0
                });
                
                modalManager.show(data.title || pluginId, data.output, { 
                    isHtml: isHtml, 
                    showCopyButton: !isHtml, 
                    copyText: data.output 
                });
            }
        } else {
            modalManager.show('Error', data.error || 'Unknown error occurred while executing plugin.', { isError: true, showCopyButton: true, copyText: data.error }); //
        }
    } catch (error) {
        console.error('Error executing plugin:', error);
        modalManager.show('Client-Side Error', `Failed to execute plugin: ${error.message}`, { isError: true, showCopyButton: true, copyText: error.message }); //
    }
}

// Handle dropdown option selection for V2 plugins
document.addEventListener('click', function(e) {
    const dropdownOption = e.target.closest('.dropdown-option');
    
    if (dropdownOption) {
        // Handle dropdown option selection
        const action = dropdownOption.dataset.action;
        const wrapper = dropdownOption.closest('.toolbar-item-wrapper');
        const button = wrapper.querySelector('.toolbar-item');
        const pluginId = button.dataset.pluginId;
        const currentPath = button.dataset.currentPath;
        
        // Hide dropdown
        wrapper.querySelector('.toolbar-dropdown').classList.add('hidden');
        
        if (action === 'page') {
            // Navigate to plugin page with folder constraint
            const url = `/plugin/${pluginId}?path=${encodeURIComponent(currentPath)}`;
            window.location.href = url;
        } else {
            // Standard modal execution
            executePlugin(pluginId, currentPath);
        }
        
        e.stopPropagation();
        return;
    }
});

// Hide dropdowns when clicking elsewhere
document.addEventListener('click', function(e) {
    if (!e.target.closest('.toolbar-item-wrapper')) {
        document.querySelectorAll('.toolbar-dropdown').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
    }
});

// Handle keyboard navigation for dropdowns
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        document.querySelectorAll('.toolbar-dropdown').forEach(dropdown => {
            dropdown.classList.add('hidden');
        });
    }
});

// Enhanced executePlugin function for V2 support
window.executePluginV2 = async function(pluginId, path, mode = 'modal') {
    if (mode === 'page') {
        // Navigate to plugin page
        const url = `/plugin/${pluginId}?path=${encodeURIComponent(path)}`;
        window.location.href = url;
        return;
    }
    
    // Use existing modal execution
    return executePlugin(pluginId, path);
};