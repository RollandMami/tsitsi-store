/**
 * Tsitsi Store - Système de notifications & Immersion iOS (Cupertino)
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. FONCTION DE LECTURE DU SON ---
    function playNotificationSound() {
        const sound = document.getElementById('ios-notification-sound');
        if (sound) {
            // Reset le son s'il est déjà en train de jouer (pour les clics rapides)
            sound.currentTime = 0;
            sound.volume = 0.4; // Volume doux
            
            // Tentative de lecture
            sound.play().catch(error => {
                // Les navigateurs bloquent l'audio sans interaction préalable
                console.log("Audio en attente d'interaction utilisateur.");
            });
        }
    }

    // --- 2. INITIALISATION DES TOASTS BOOTSTRAP ---
    // Ces toasts utilisent la structure HTML définie dans base.html
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function(toastEl) {
        
        // Configuration Bootstrap Toast
        const t = new bootstrap.Toast(toastEl, { 
            autohide: true, 
            delay: 5000 // Disparait après 5 secondes
        });

        // Jouer le son iOS à l'apparition si le toast est affiché au chargement
        if (toastEl.classList.contains('show')) {
            playNotificationSound();
        }

        // Écouteur pour jouer le son si le toast est déclenché dynamiquement
        toastEl.addEventListener('show.bs.toast', function() {
            playNotificationSound();
        });

        t.show();
        return t;
    });

    // --- 3. SYSTÈME DE POP-UP DE SUPPRESSION (SweetAlert2) ---
    // Transforme les alertes SweetAlert en boîtes de dialogue Apple
    window.confirmDelete = function(url) {
        // Petit retour sonore lors de l'ouverture de l'alerte
        playNotificationSound();

        Swal.fire({
            title: 'Confirmation',
            text: "Voulez-vous vraiment supprimer cet élément ?",
            showCancelButton: true,
            confirmButtonText: 'Supprimer',
            cancelButtonText: 'Annuler',
            reverseButtons: true, // Bouton bleu à gauche, rouge à droite (style iOS)
            buttonsStyling: false,
            background: 'rgba(255, 255, 255, 0.9)', // Glassmorphism
            backdrop: `rgba(0,0,0,0.4) blur(6px)`, // Flou d'arrière-plan
            customClass: {
                popup: 'cupertino-swal-popup',
                confirmButton: 'cupertino-swal-confirm',
                cancelButton: 'cupertino-swal-cancel',
                title: 'cupertino-swal-title',
                htmlContainer: 'cupertino-swal-text'
            }
        }).then((result) => {
            if (result.isConfirmed) {
                // Petit délai pour laisser l'animation se finir
                window.location.href = url;
            }
        });
    }

    // --- 4. GESTION DES CLICS POUR DÉBLOQUER L'AUDIO ---
    // Force le déblocage du contexte audio sur mobile au premier clic sur la page
    document.body.addEventListener('click', function() {
        const sound = document.getElementById('ios-notification-sound');
        if (sound && sound.paused) {
            sound.muted = true; // Joue en muet une fois pour débloquer
            sound.play().then(() => {
                sound.pause();
                sound.muted = false;
            });
        }
    }, { once: true });

});