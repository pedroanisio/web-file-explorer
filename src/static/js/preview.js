// Preview pane functionality

document.addEventListener('DOMContentLoaded', () => {
  const previewPane = document.getElementById('preview-pane');
  const previewFrame = document.getElementById('preview-frame');
  const toggleBtn = document.getElementById('toggle-preview-pane');
  const closeBtn = document.getElementById('close-preview');
  const loading = document.getElementById('preview-loading');

  function setVisible(show) {
    if (show) {
      previewPane.classList.remove('hidden');
      localStorage.setItem('previewPaneVisible', 'true');
    } else {
      previewPane.classList.add('hidden');
      localStorage.setItem('previewPaneVisible', 'false');
    }
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      setVisible(previewPane.classList.contains('hidden'));
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', () => setVisible(false));
  }

  const stored = localStorage.getItem('previewPaneVisible');
  if (stored === 'true') {
    setVisible(true);
  }

  document.querySelectorAll('.preview-link').forEach(link => {
    link.addEventListener('click', e => {
      e.preventDefault();
      const url = link.getAttribute('data-preview-url');
      if (!url) return;
      setVisible(true);
      loading.classList.remove('hidden');
      previewFrame.classList.add('hidden');
      previewFrame.onload = () => {
        loading.classList.add('hidden');
        previewFrame.classList.remove('hidden');
      };
      previewFrame.src = url;
    });
  });
});
