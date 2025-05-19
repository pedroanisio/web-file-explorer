document.addEventListener('DOMContentLoaded', () => {
    const favoritesBar = document.getElementById('favorites-bar');
    const addFavoriteBtn = document.getElementById('add-favorite-btn');
    
    // Log a warning if key elements aren't found
    if (!favoritesBar) {
        console.warn('Favorites bar (#favorites-bar) not found in the DOM - favorites feature will be disabled');
    }
    
    if (!addFavoriteBtn) {
        console.warn('Add favorite button (#add-favorite-btn) not found in the DOM - adding favorites will be disabled');
    }

    function loadFavorites() {
        // Only try to load favorites if we have the favorites bar element
        if (!favoritesBar) {
            console.warn('Favorites bar element not found, cannot load favorites');
            return;
        }
        
        const favs = JSON.parse(localStorage.getItem('favorites') || '[]');
        renderFavorites(favs);
    }

    function saveFavorites(favs) {
        localStorage.setItem('favorites', JSON.stringify(favs));
    }

    function renderFavorites(favs) {
        // Check if favoritesBar exists before trying to modify it
        if (!favoritesBar) {
            console.warn('Favorites bar element not found in DOM');
            return;
        }
        
        favoritesBar.innerHTML = '';
        
        if (!favs.length) {
            favoritesBar.style.display = 'none';
            return;
        }
        
        favoritesBar.style.display = 'flex';
        
        favs.forEach(path => {
            // Create element first with opacity 0 for animation
            const item = document.createElement('div');
            item.className = 'favorite-item flex items-center gap-1 px-3 py-2 rounded-lg bg-gray-200 dark:bg-gray-700 transition-all';
            item.style.opacity = '0';
            item.style.transform = 'translateY(10px)';

            // Get just the folder name from the path
            let displayName = path || 'Home';
            if (displayName !== 'Home') {
                // Get last segment of the path
                const segments = displayName.split('/').filter(Boolean);
                displayName = segments.length > 0 ? segments[segments.length - 1] : displayName;
            }

            // Create link with icon
            const link = document.createElement('a');
            link.href = `/explore/${path}`;
            link.className = 'text-blue-600 dark:text-blue-400 hover:underline flex items-center';
            
            // Add folder icon
            if (path === '') {
                link.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-blue-500 dark:text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                    </svg>
                    Home
                `;
            } else {
                link.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-yellow-500 dark:text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
                    </svg>
                    ${displayName}
                `;
            }
            
            item.appendChild(link);

            // Create remove button
            const remove = document.createElement('button');
            remove.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            `;
            remove.className = 'remove-favorite ml-1 p-1 rounded-full hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors';
            remove.setAttribute('title', 'Remove from favorites');
            remove.setAttribute('aria-label', 'Remove from favorites');
            remove.dataset.path = path;
            item.appendChild(remove);

            favoritesBar.appendChild(item);
            
            // Animate in with a slight delay based on index
            setTimeout(() => {
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50);
        });
    }

    favoritesBar?.addEventListener('click', e => {
        // Handle clicking on the remove button
        if (e.target.closest('.remove-favorite')) {
            const button = e.target.closest('.remove-favorite');
            const path = button.dataset.path;
            const item = button.closest('.favorite-item');
            
            // Animate removal
            item.style.opacity = '0';
            item.style.transform = 'translateY(10px)';
            
            setTimeout(() => {
                let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
                favs = favs.filter(p => p !== path);
                saveFavorites(favs);
                renderFavorites(favs);
                
                // Show feedback toast
                showToast('Favorite removed');
            }, 300);
        }
    });

    addFavoriteBtn?.addEventListener('click', () => {
        const path = addFavoriteBtn.dataset.currentPath || '';
        let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
        
        if (!favs.includes(path)) {
            // Add the favorite with animation
            favs.push(path);
            saveFavorites(favs);
            
            // Re-render the favorites list
            renderFavorites(favs);
            
            // Add pulse animation to the button
            addFavoriteBtn.classList.add('animate-pulse');
            setTimeout(() => {
                addFavoriteBtn.classList.remove('animate-pulse');
            }, 1000);
            
            // Show feedback toast
            showToast('Added to favorites');
        } else {
            // Already a favorite - provide feedback
            showToast('Already in favorites', true);
            
            // Shake the button
            addFavoriteBtn.classList.add('shake');
            setTimeout(() => {
                addFavoriteBtn.classList.remove('shake');
            }, 800);
        }
    });
    
    function showToast(message, isWarning = false) {
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
        toast.className = `py-2 px-4 rounded-lg shadow-lg mb-3 flex items-center gap-2 transition-all duration-300 transform translate-x-full ${
            isWarning 
                ? 'bg-amber-500 dark:bg-amber-600 text-white' 
                : 'bg-green-500 dark:bg-green-600 text-white'
        }`;
        
        // Add icon
        if (isWarning) {
            toast.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            `;
        } else {
            toast.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
            `;
        }
        
        // Add message
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        toast.appendChild(messageSpan);
        
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
                if (toast.parentNode) {
                    toastContainer.removeChild(toast);
                }
                // If no more toasts, remove container
                if (toastContainer.children.length === 0) {
                    document.body.removeChild(toastContainer);
                }
            }, 300);
        }, 3000);
    }
    
    // Add shake animation style
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        .shake {
            animation: shake 0.8s cubic-bezier(.36,.07,.19,.97) both;
        }
        .favorite-item {
            transition: opacity 0.3s ease, transform 0.3s ease;
        }
        .animate-pulse {
            animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: .5; }
        }
    `;
    document.head.appendChild(style);

    // Load favorites on page load
    loadFavorites();
});