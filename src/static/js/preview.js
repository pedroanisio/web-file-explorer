// Preview pane functionality with improved UI handling

document.addEventListener('DOMContentLoaded', () => {
  const previewPane = document.getElementById('preview-pane');
  const previewFrame = document.getElementById('preview-frame');
  const toggleBtn = document.getElementById('toggle-preview-pane');
  const closeBtn = document.getElementById('close-preview');
  const loading = document.getElementById('preview-loading');

  // Function to show/hide preview pane with animation
  function setVisible(show) {
    if (show) {
      // First make it display: block but opacity 0
      previewPane.classList.remove('hidden');
      previewPane.style.opacity = '0';
      
      // Then trigger animation
      setTimeout(() => {
        previewPane.style.opacity = '1';
        
        // Add transition property temporarily
        previewPane.style.transition = 'opacity 0.3s ease';
        
        // Store preference
        localStorage.setItem('previewPaneVisible', 'true');
        
        // Reset transition after animation completes
        setTimeout(() => {
          previewPane.style.transition = '';
        }, 300);
      }, 10);
    } else {
      // Animate out
      previewPane.style.transition = 'opacity 0.3s ease';
      previewPane.style.opacity = '0';
      
      // Then hide
      setTimeout(() => {
        previewPane.classList.add('hidden');
        previewPane.style.transition = '';
        localStorage.setItem('previewPaneVisible', 'false');
      }, 300);
    }
    
    // Update toggle button text
    if (toggleBtn) {
      toggleBtn.innerHTML = show ? 
        `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-14-14zm14 1.414a1 1 0 00-1.414-1.414L5.707 12.879a1 1 0 101.414 1.414l10.586-10.586z" clip-rule="evenodd" />
        </svg>Hide Preview` : 
        `<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
          <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
        </svg>Preview`;
    }
  }

  // Toggle preview pane when button is clicked
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      setVisible(previewPane.classList.contains('hidden'));
    });
  }

  // Close preview pane when close button is clicked
  if (closeBtn) {
    closeBtn.addEventListener('click', () => setVisible(false));
  }

  // Load saved preference
  const stored = localStorage.getItem('previewPaneVisible');
  if (stored === 'true') {
    setVisible(true);
  }

  // Attach event listeners to preview links
  document.querySelectorAll('.preview-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const url = link.getAttribute('data-preview-url');
      const fileName = link.closest('tr').querySelector('a').textContent.trim();
      
      if (!url) return;
      
      // Show preview pane
      setVisible(true);
      
      // Show loading indicator, hide iframe
      loading.classList.remove('hidden');
      previewFrame.classList.add('hidden');
      
      // Update preview pane title if possible
      const cardTitle = document.querySelector('#preview-pane .card-title');
      if (cardTitle && fileName) {
        cardTitle.textContent = 'Preview: ' + fileName;
        // Also update iframe title for better accessibility
        previewFrame.setAttribute('title', `Preview of ${fileName}`);
      }
      
      // Set up iframe load event
      previewFrame.onload = () => {
        loading.classList.add('hidden');
        previewFrame.classList.remove('hidden');
        
        // Adjust height in mobile view
        if (window.innerWidth < 768) {
          previewFrame.style.height = '300px';
        } else {
          previewFrame.style.height = '500px';
        }
      };
      
      // Load content
      previewFrame.src = url;
    });
  });
  
  // Handle responsive adjustments on window resize
  window.addEventListener('resize', () => {
    if (!previewPane.classList.contains('hidden') && previewFrame) {
      if (window.innerWidth < 768) {
        previewFrame.style.height = '300px';
      } else {
        previewFrame.style.height = '500px';
      }
    }
  });
});