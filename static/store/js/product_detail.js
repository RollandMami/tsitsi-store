document.addEventListener('DOMContentLoaded', function() {
        
        // === 1. GESTION DE LA GALERIE ===
        const mainImg = document.getElementById('mainImage');
        const thumbnails = document.querySelectorAll('.miniature-img');
        
        if (mainImg && thumbnails.length > 0) {
            thumbnails.forEach(thumb => {
                thumb.addEventListener('click', function() {
                    mainImg.src = this.src;
                    thumbnails.forEach(t => t.classList.remove('active-mini'));
                    this.classList.add('active-mini');
                });
            });
        }

        // === 2. GESTION DU SYSTÈME DE NOTATION (ÉTOILES) ===
        const stars = document.querySelectorAll('.star-icon');
        const ratingInput = document.getElementById('id_rating_value');

        if (stars.length > 0 && ratingInput) {
            stars.forEach(star => {
                // Au clic sur une étoile
                star.addEventListener('click', function() {
                    const value = this.getAttribute('data-value');
                    
                    // On met à jour l'input caché pour Django
                    ratingInput.value = value;

                    // On met à jour le visuel des étoiles
                    stars.forEach(s => {
                        if (parseInt(s.getAttribute('data-value')) <= parseInt(value)) {
                            s.classList.remove('text-muted');
                            s.classList.add('text-warning');
                        } else {
                            s.classList.remove('text-warning');
                            s.classList.add('text-muted');
                        }
                    });
                });

                // Effet au survol (facultatif mais sympa)
                star.addEventListener('mouseover', function() {
                    this.style.transform = "scale(1.2)";
                    this.style.transition = "transform 0.2s";
                });
                star.addEventListener('mouseout', function() {
                    this.style.transform = "scale(1)";
                });
            });
        }
        
        // === 3. VÉRIFICATION AVANT ENVOI DU FORMULAIRE ===
        const reviewForm = document.querySelector('form[action*="submit_review"]');
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                if (!ratingInput.value || ratingInput.value === "0") {
                    e.preventDefault();
                    alert("Veuillez sélectionner une note avant de publier votre avis.");
                }
            });
        }
    });