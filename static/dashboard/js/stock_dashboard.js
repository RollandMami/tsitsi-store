// 1. Déclarations globales
let stockModal;
let stockToast;
let table;

$(document).ready(function() {
    // 2. Initialisation de DataTable (Version avec marges et style moderne)
    table = $('#stockTable').DataTable({
        "language": {
            "url": "//cdn.datatables.net/plug-ins/1.13.6/i18n/fr-FR.json",
            "search": "", 
            "searchPlaceholder": "Rechercher un produit..."
        },
        "pageLength": 10,
        "order": [[2, "desc"]], // Tri par quantité (3ème colonne) par défaut
        "columnDefs": [
            { "orderable": false, "targets": [0, 4] } // Désactive le tri sur Image et Actions
        ],
        // Structure aérée avec classes Bootstrap (px-4 py-3)
        "dom": '<"d-flex justify-content-between align-items-center px-4 py-3"f>t<"d-flex justify-content-between align-items-center px-4 py-3"ip>'
    });

    // 3. Initialisation des composants Bootstrap
    stockModal = new bootstrap.Modal(document.getElementById('stockModal'));
    stockToast = new bootstrap.Toast(document.getElementById('stockToast'));

    // 4. Gestion du clic sur le bouton "+" (Délégation d'événement jQuery)
    // Fonctionne même après une recherche ou un changement de page
    $(document).on('click', '.edit-stock-btn', function() {
        const btn = $(this);
        const id = btn.data('id');
        const name = btn.data('name');
        const stock = btn.data('stock');

        $('#productId').val(id);
        $('#modalProductName').text(name);
        $('#newStockInput').val(stock);
        
        stockModal.show();
    });
});

// 5. Envoi des données vers Django (AJAX)
document.getElementById('stockForm').onsubmit = function(e) {
    e.preventDefault();
    const id = document.getElementById('productId').value;
    const newStock = parseInt(document.getElementById('newStockInput').value);

    fetch("{% url 'dashboard:update_stock_ajax' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({ "id": id, "new_stock": newStock })
    })
    .then(response => {
        if (!response.ok) throw new Error('Erreur réseau');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            stockModal.hide();
            
            // Mise à jour visuelle immédiate du texte de quantité
            const qtySpan = document.getElementById(`qty-text-${id}`);
            if (qtySpan) qtySpan.innerText = newStock;
            
            // Mise à jour de l'attribut data-stock du bouton pour le prochain clic
            const btn = document.querySelector(`.edit-stock-btn[data-id="${id}"]`);
            if (btn) btn.dataset.stock = newStock;

            stockToast.show();
            
            // Recharger après 1.5s pour actualiser les compteurs (Total, Rupture, etc.)
            setTimeout(() => { location.reload(); }, 1500);
        } else {
            alert("Erreur: " + data.error);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert("Une erreur est survenue lors de la mise à jour.");
    });
};