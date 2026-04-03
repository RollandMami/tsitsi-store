document.addEventListener('DOMContentLoaded', function() {
    // 1. Prévisualisation dynamique des images
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                const wrapper = this.closest('.image-preview-wrapper') || this.closest('.collaborator-img-wrapper');
                let img = wrapper.querySelector('.preview-img');
                
                reader.onload = function(e) {
                    if (!img) {
                        img = document.createElement('img');
                        img.classList.add('preview-img');
                        wrapper.insertBefore(img, input);
                    }
                    img.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    });

    // 2. Boutons d'ajout dynamique pour les Formsets
    setupFormsetAdd('add-timeline-btn', 'timeline-table-body', 'events');
    setupFormsetAdd('add-member-btn', 'team-grid-body', 'members');
});

function setupFormsetAdd(btnId, bodyId, prefix) {
    const btn = document.getElementById(btnId);
    const body = document.getElementById(bodyId);
    const totalFormsInput = document.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);
    
    if (!btn || !body || !totalFormsInput) return;

    btn.addEventListener('click', function() {
        const currentCount = parseInt(totalFormsInput.value);
        const forms = body.querySelectorAll('.formset-row');
        
        if (forms.length === 0) return;

        // Clone la dernière ligne
        const newRow = forms[forms.length - 1].cloneNode(true);
        
        // Remplace les indices dans les attributs name et id
        newRow.innerHTML = newRow.innerHTML.replace(new RegExp(`${prefix}-\\d+-`, 'g'), `${prefix}-${currentCount}-`);
        
        // Nettoie les valeurs du clone
        newRow.querySelectorAll('input:not([type="hidden"]), textarea').forEach(input => {
            if (input.type === 'checkbox') input.checked = true;
            else input.value = '';
        });
        
        // Nettoie l'image si elle existe dans le clone
        const clonedImg = newRow.querySelector('.preview-img');
        if (clonedImg) clonedImg.remove();
        
        body.appendChild(newRow);
        totalFormsInput.value = currentCount + 1;
    });
}