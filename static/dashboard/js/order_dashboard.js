
    // 1. RECHERCHE AJAX (input dans le header)
    const searchInput = document.getElementById('orderSearchInput');
    const tableBody = document.getElementById('orderTableBody');
    let searchTimeout;

    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value;

            // On attend 300ms après la dernière touche pour envoyer la requête (Debounce)
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                
                // On ajoute un effet visuel de chargement
                tableBody.classList.add('loading-fade');

                fetch(`?q=${encodeURIComponent(query)}`, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(res => {
                    if (!res.ok) throw new Error('Erreur serveur');
                    return res.json();
                })
                .then(data => {
                    // On remplace le contenu du tableau
                    tableBody.innerHTML = data.html;
                    
                    // On retire l'effet de chargement
                    tableBody.classList.remove('loading-fade');

                    // TRÈS IMPORTANT : On ré-initialise les événements sur les nouveaux éléments
                    initStatusChange(); 
                    initDeleteButtons(); 
                })
                .catch(err => {
                    console.error('Erreur recherche:', err);
                    tableBody.classList.remove('loading-fade');
                });
            }, 300);
        });
    }

    // Fonction pour ré-initialiser les boutons de suppression après une recherche AJAX
    function initDeleteButtons() {
        const deleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        document.querySelectorAll('.btn-trigger-delete').forEach(btn => {
            btn.onclick = function() {
                window.formToSubmit = this.closest('form');
                deleteModal.show();
            };
        });
    }

    // 2. CHANGEMENT DE STATUT SANS RECHARGEMENT
    function initStatusChange() {
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', function() {
                const orderId = this.dataset.orderId;
                const newStatus = this.value;
                
                fetch(`/dashboard/orders/update/${orderId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: `status=${encodeURIComponent(newStatus)}`
                })
                .then(response => response.json())
                .then(data => {
                    // Attendu: {status: 'success'|'error', message: '...'}
                    if (data.status === 'success') {
                        showToast(data.message || 'Statut mis à jour', 'Succès', 'success');
                    } else {
                        showToast(data.message || 'Erreur lors de la mise à jour du statut.', 'Erreur', 'danger');
                    }
                })
                .catch(err => {
                    console.error('Erreur AJAX:', err);
                    showToast('Erreur réseau lors de la mise à jour du statut.', 'Erreur', 'danger');
                });
            });
        });
    }
    initStatusChange();

    // Initialiser le graphique au chargement
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPerformanceChart);
    } else {
        initPerformanceChart();
    }

    // Fonction pour obtenir le cookie CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }