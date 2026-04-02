 document.addEventListener('DOMContentLoaded', function() {
        // 1. Filtrage dynamique (Nom + Catégorie)
        const searchInput = document.getElementById('searchStock');
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                const term = e.target.value.toLowerCase();
                const rows = document.querySelectorAll('.product-row');
                
                rows.forEach(row => {
                    const name = row.querySelector('.product-name').textContent.toLowerCase();
                    const category = row.querySelector('.product-category').textContent.toLowerCase();
                    const isVisible = name.includes(term) || category.includes(term);
                    row.style.display = isVisible ? '' : 'none';
                });
            });
        }

        // 2. Gestion de la Modale via Bootstrap API
        const stockModalEl = document.getElementById('stockModal');
        const stockModal = new bootstrap.Modal(stockModalEl);

        window.openStockModal = function(id, name, currentStock) {
            document.getElementById('modalProductId').value = id;
            document.getElementById('modalProductName').textContent = name;
            document.getElementById('modalStockValue').value = currentStock;
            stockModal.show();
            
            // Focus automatique sur l'input
            stockModalEl.addEventListener('shown.bs.modal', function () {
                document.getElementById('modalStockValue').focus();
            }, { once: true });
        };
    });