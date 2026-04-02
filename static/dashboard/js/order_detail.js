document.addEventListener('DOMContentLoaded', function() {
    const statusForm = document.getElementById('statusForm');
    if (statusForm) {
      statusForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const url = this.action;
        const formData = new FormData(this);
        // show a simple loading state (disable btn)
        const submitBtn = this.querySelector('button[type=submit]');
        submitBtn.disabled = true;

        fetch(url, {
          method: 'POST',
          headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: formData
        })
          .then(response => {
            if (!response.ok) {
              throw new Error("Erreur serveur (Code: " + response.status + ")");
            }
            return response.json();
          })
          .then(data => {
            submitBtn.disabled = false;
            // afficher le message dans la modal
            const body = document.getElementById('statusModalBody');
            body.textContent = data.message || 'Statut mis à jour avec succès !';
            const statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
            statusModal.show();
          })
          .catch(err => {
            submitBtn.disabled = false;
            const body = document.getElementById('statusModalBody');
            body.textContent = 'Erreur :' + err.message;
            const statusModal = new bootstrap.Modal(document.getElementById('statusModal'));
            statusModal.show();
          });
      });
    }
  });