(function() {
    //console.log("Recherche avec Highlight activée !");

    const initLiveSearch = () => {
        const searchInput = document.getElementById('search-input-mobile');
        if (!searchInput) return;

        // Stocker les titres originaux pour pouvoir les restaurer
        const originalTitles = new Map();
        const productElements = document.querySelectorAll('.product-item, .product-card');
        
        productElements.forEach((el, index) => {
            const titleEl = el.querySelector('.card-title, h6');
            if (titleEl) {
                originalTitles.set(el, titleEl.innerHTML);
            }
        });

        searchInput.addEventListener('input', function() {
            const searchTerm = searchInput.value.toLowerCase().trim();
            
            productElements.forEach(product => {
                const titleElement = product.querySelector('.card-title, h6');
                const container = product.closest('.col');
                
                if (titleElement && container) {
                    const originalHTML = originalTitles.get(product);
                    const textContent = titleElement.innerText;
                    
                    if (searchTerm === "") {
                        // Si vide, on restaure tout
                        titleElement.innerHTML = originalHTML;
                        container.style.setProperty('display', 'block', 'important');
                        return;
                    }

                    if (textContent.toLowerCase().includes(searchTerm)) {
                        // 1. Afficher le produit
                        container.style.setProperty('display', 'block', 'important');
                        
                        // 2. Mettre en surbrillance (Highlight)
                        const regex = new RegExp(`(${searchTerm})`, 'gi');
                        titleElement.innerHTML = textContent.replace(regex, '<mark style="background-color: #ffeb3b; padding: 0; border-radius: 2px;">$1</mark>');
                    } else {
                        // Cacher le produit
                        container.style.setProperty('display', 'none', 'important');
                    }
                }
            });
        });
    };

    if (document.readyState === 'complete') {
        initLiveSearch();
    } else {
        window.addEventListener('load', initLiveSearch);
    }
})();