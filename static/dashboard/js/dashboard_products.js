document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('ajax-search');
        const resultsTable = document.getElementById('product-table-body');
        const searchIcon = document.getElementById('search-icon');
        const badge = document.getElementById('product-count');
        let timeout = null;

        if (searchInput) {
            searchInput.addEventListener('keyup', function() {
                // Annule le timer précédent (Debounce)
                clearTimeout(timeout);
                
                timeout = setTimeout(() => {
                    const query = searchInput.value;
                    
                    // Indicateur visuel de chargement
                    resultsTable.classList.add('loading-fade');
                    searchIcon.className = 'fas fa-spinner fa-spin';

                    fetch(`{% url 'dashboard:products' %}?q=${query}`, {
                        headers: { 'X-Requested-With': 'XMLHttpRequest' }
                    })
                    .then(response => response.json())
                    .then(data => {
                        resultsTable.innerHTML = data.html;
                        if (badge) badge.innerText = data.count;
                        
                        // Réinitialise les indicateurs
                        resultsTable.classList.remove('loading-fade');
                        searchIcon.className = 'fas fa-search';
                    })
                    .catch(error => {
                        console.error('Erreur:', error);
                        searchIcon.className = 'fas fa-search';
                    });
                }, 300); // 300ms de délai
            });
        }
    });

    const CSRF_TOKEN = '{{ csrf_token }}';
// --- FONCTIONS UTILITAIRES ---
function previewImage(input, id) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) { 
            document.getElementById('preview-' + id).src = e.target.result; 
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function showNotification(message, type = 'success') {
    const toastEl = document.getElementById('liveToast');
    const toastMessage = document.getElementById('toastMessage');
    const toastIcon = document.getElementById('toastIcon');
    toastEl.classList.remove('bg-danger', 'bg-success');
    
    if (type === 'success') {
        toastEl.classList.add('bg-success');
        toastIcon.className = 'fas fa-check-circle me-2';
    } else {
        toastEl.classList.add('bg-danger');
        toastIcon.className = 'fas fa-exclamation-circle me-2';
    }
    toastMessage.innerText = message;
    new bootstrap.Toast(toastEl).show();
}

// --- ACTIONS AJAX ---
window.saveProduct = function(productId, csrfToken) {
    const row = document.getElementById(`row-${productId}`);
    const btn = row.querySelector('.btn-save');
    const originalIcon = btn.innerHTML;
    const formData = new FormData();
    
    row.querySelectorAll('.edit-input').forEach(input => {
        if (input.type === 'file') {
            if (input.files[0]) formData.append('images', input.files[0]);
        } else {
            formData.append(input.dataset.field, input.value);
        }
    });

    if (confirm("Enregistrer les modifications ?")) {
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        fetch(`/dashboard/products/update/${productId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                btn.classList.add('d-none');
                row.querySelectorAll('.edit-input').forEach(i => i.classList.remove('border-warning'));
                showNotification("Produit mis à jour avec succès !");
            } else {
                showNotification("Erreur: " + data.message, 'error');
            }
        })
        .catch(() => showNotification("Erreur réseau", 'error'))
        .finally(() => {
            btn.disabled = false;
            btn.innerHTML = originalIcon;
        });
    }
};

window.deleteProduct = function(productId, csrfToken) {
    if (confirm("⚠️ Supprimer définitivement ce produit ?")) {
        fetch(`/dashboard/products/delete/${productId}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(`row-${productId}`).remove();
                const countBadge = document.getElementById('product-count');
                if (countBadge) countBadge.innerText = parseInt(countBadge.innerText) - 1;
                showNotification("Le produit a été supprimé.");
            }
        });
    }
};

// --- INITIALISATION ---
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('ajax-search');
    const tableBody = document.getElementById('product-table-body');
    const countBadge = document.getElementById('product-count');

    if (searchInput && tableBody) {
        searchInput.addEventListener('input', function() {
            const keyword = encodeURIComponent(this.value);
            
            fetch(`?keyword=${keyword}`, {
                headers: {
                    'x-requested-with': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Erreur réseau');
                return response.json();
            })
            .then(data => {
                // Mise à jour du tableau
                tableBody.innerHTML = data.html;
                // Mise à jour du compteur
                if (countBadge && data.count !== undefined) {
                    countBadge.innerText = data.count;
                }
            })
            .catch(error => {
                console.error('Erreur lors de la recherche AJAX:', error);
            });
        });
    }

    // Détection des changements
    document.addEventListener('change', function(e) {
        if (e.target.classList.contains('edit-input')) {
            const row = e.target.closest('tr');
            const btn = row.querySelector('.btn-save');
            if(btn) btn.classList.remove('d-none');
            e.target.classList.add('border-warning');
        }
    });
});