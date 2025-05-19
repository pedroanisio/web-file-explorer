document.addEventListener('DOMContentLoaded', () => {
    const favoritesBar = document.getElementById('favorites-bar');
    const addFavoriteBtn = document.getElementById('add-favorite-btn');

    function loadFavorites() {
        const favs = JSON.parse(localStorage.getItem('favorites') || '[]');
        renderFavorites(favs);
    }

    function saveFavorites(favs) {
        localStorage.setItem('favorites', JSON.stringify(favs));
    }

    function renderFavorites(favs) {
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
