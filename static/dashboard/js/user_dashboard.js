// Recherche AJAX responsive
document.getElementById('user-search-form').addEventListener('submit', function(e){
  e.preventDefault();
  const q = this.q.value;
  fetch(`${location.pathname}?q=${encodeURIComponent(q)}`, {
    headers: {'x-requested-with': 'XMLHttpRequest'}
  })
    .then(r => r.json())
    .then(data => {
      document.getElementById('user-table-container').innerHTML = data.html;
    })
    .catch(err => console.error('Erreur AJAX:', err));
});

// Activer/désactiver utilisateur
function toggleUser(pk, field, el){
  const val = el.checked ? 'True' : 'False';
  const fd = new FormData();
  fd.append(field, val);

  fetch(`/dashboard/clients/update/${pk}/`, {
    method: 'POST', 
    body: fd, 
    headers: {'X-CSRFToken': getCookie('csrftoken')}
  })
    .then(r => r.json())
    .then(data => {
      if(data.status !== 'success') {
        alert(data.message || 'Erreur lors de la mise à jour');
        el.checked = !el.checked;
      }
    })
    .catch(err => {
      console.error('Erreur:', err);
      el.checked = !el.checked;
      alert('Erreur réseau');
    });
}

// Supprimer utilisateur avec confirmation
function deleteUser(pk){
  if(!confirm('⚠️ Êtes-vous sûr de vouloir supprimer cet utilisateur ? Cette action est irréversible.')) return;
  
  const fd = new FormData();
  fetch(`/dashboard/clients/delete/${pk}/`, {
    method: 'POST', 
    body: fd, 
    headers: {'X-CSRFToken': getCookie('csrftoken')}
  })
    .then(r => r.json())
    .then(data => {
      if(data.status === 'success') {
        location.reload();
      } else {
        alert(data.message || 'Erreur lors de la suppression');
      }
    })
    .catch(err => {
      console.error('Erreur:', err);
      alert('Erreur réseau');
    });
}

// Accéder à la page d'édition
function editUser(pk){
  window.location.href = `/dashboard/clients/edit/${pk}/`;
}

// Obtenir le cookie CSRF
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