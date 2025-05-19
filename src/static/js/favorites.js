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
            const item = document.createElement('div');
            item.className = 'favorite-item flex items-center gap-1 px-2 py-1 rounded bg-gray-200 dark:bg-gray-700';

            const link = document.createElement('a');
            link.href = `/explore/${path}`;
            link.textContent = path || 'Home';
            link.className = 'text-blue-600 dark:text-blue-400 hover:underline';
            item.appendChild(link);

            const remove = document.createElement('button');
            remove.textContent = '×';
            remove.className = 'remove-favorite text-red-600 hover:text-red-800';
            remove.dataset.path = path;
            item.appendChild(remove);

            favoritesBar.appendChild(item);
        });
    }

    favoritesBar?.addEventListener('click', e => {
        if (e.target.classList.contains('remove-favorite')) {
            const path = e.target.dataset.path;
            let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
            favs = favs.filter(p => p !== path);
            saveFavorites(favs);
            renderFavorites(favs);
        }
    });

    addFavoriteBtn?.addEventListener('click', () => {
        const path = addFavoriteBtn.dataset.currentPath || '';
        let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
        if (!favs.includes(path)) {
            favs.push(path);
            saveFavorites(favs);
            renderFavorites(favs);
        }
    });

    loadFavorites();
});
