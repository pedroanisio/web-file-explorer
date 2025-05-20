document.addEventListener('DOMContentLoaded', () => {
    const favoritesBar = document.getElementById('favorites-bar');
    const addFavoriteBtn = document.getElementById('add-favorite-btn');

    if (!favoritesBar) {
        console.warn('Favorites bar (#favorites-bar) not found.'); //
    }
    if (!addFavoriteBtn) {
        console.warn('Add favorite button (#add-favorite-btn) not found.'); //
    }

    function loadFavorites() {
        if (!favoritesBar) return; //
        const favs = JSON.parse(localStorage.getItem('favorites') || '[]'); //
        renderFavorites(favs);
    }

    function saveFavorites(favs) {
        localStorage.setItem('favorites', JSON.stringify(favs)); //
    }

    function renderFavorites(favs) {
        if (!favoritesBar) return; //
        favoritesBar.innerHTML = ''; //
        if (!favs.length) {
            favoritesBar.style.display = 'none'; //
            return;
        }

        favoritesBar.style.display = 'flex'; //
        favs.forEach((path, index) => {
            const item = document.createElement('div');
            // Styling for favorite-item is in components.css
            item.className = 'favorite-item'; //
            item.style.opacity = '0';
            item.style.transform = 'translateY(10px)';

            let displayName = path || 'Home'; //
            if (displayName !== 'Home') {
                const segments = displayName.split('/').filter(Boolean);
                displayName = segments.length > 0 ? segments[segments.length - 1] : displayName; //
            }

            const link = document.createElement('a');
            link.href = `/explore/${path}`;
            // Styling for link is in components.css
            // link.className = 'text-blue-600 dark:text-blue-400 hover:underline flex items-center';

            const iconClass = path === '' ? 'text-blue-500 dark:text-blue-400' : 'text-yellow-500 dark:text-yellow-400';
            const iconPath = path === '' 
                ? "M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" //
                : "M2 6a2 2 0 012-2h5l2 2h5a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6z"; //

            link.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 ${iconClass}" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="${iconPath}" clip-rule="evenodd" />
                </svg>
                ${displayName}
            `; //
            item.appendChild(link);

            const remove = document.createElement('button');
            remove.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
            `; //
            // Styling for remove-favorite is in components.css
            remove.className = 'remove-favorite'; //
            remove.setAttribute('title', 'Remove from favorites');
            remove.setAttribute('aria-label', 'Remove from favorites');
            remove.dataset.path = path;
            item.appendChild(remove);

            favoritesBar.appendChild(item);
            setTimeout(() => { // Animate in
                item.style.opacity = '1';
                item.style.transform = 'translateY(0)';
            }, 50 * index); // Stagger animation slightly
        });
    }

    if (favoritesBar) {
        favoritesBar.addEventListener('click', e => {
            const removeButton = e.target.closest('.remove-favorite');
            if (removeButton) {
                const path = removeButton.dataset.path;
                const item = removeButton.closest('.favorite-item');

                item.style.opacity = '0'; // Animate removal
                item.style.transform = 'scale(0.8)';
                item.style.marginRight = `-${item.offsetWidth}px`;


                setTimeout(() => {
                    let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
                    favs = favs.filter(p => p !== path); //
                    saveFavorites(favs);
                    renderFavorites(favs); // Re-render after modifying data
                    window.showToast('Favorite removed', 'success'); //
                }, 300);
            }
        });
    }

    if (addFavoriteBtn) {
        addFavoriteBtn.addEventListener('click', () => {
            const path = addFavoriteBtn.dataset.currentPath || '';
            let favs = JSON.parse(localStorage.getItem('favorites') || '[]');

            if (!favs.includes(path)) {
                favs.push(path); //
                saveFavorites(favs);
                renderFavorites(favs); // Re-render with animation for new item

                addFavoriteBtn.classList.add('animate-pulse-strong'); //
                setTimeout(() => {
                    addFavoriteBtn.classList.remove('animate-pulse-strong');
                }, 1500);
                window.showToast('Added to favorites', 'success'); //
            } else {
                window.showToast('Already in favorites', 'warning'); //
                addFavoriteBtn.classList.add('shake'); //
                setTimeout(() => {
                    addFavoriteBtn.classList.remove('shake');
                }, 800); //
            }
        });
    }

    // Load favorites on page load
    loadFavorites(); //
});