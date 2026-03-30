from django import forms
from .models import ReviewAndRating, ReviewImage

class ReviewForm(forms.ModelForm):
    # Utilisation de HiddenInput car le JS remplit la valeur
    # On garde les limites strictes (1 à 7) pour la sécurité serveur
    rating = forms.IntegerField(
        widget=forms.HiddenInput(), 
        min_value=1, 
        max_value=7,
        error_messages={
            'required': "Veuillez attribuer une note entre 1 et 7.",
            'invalid': "La note doit être un nombre entier.",
            'min_value': "La note minimale est de 1 étoile.",
            'max_value': "La note maximale est de 7 étoiles.",
        }
    )
    
    class Meta:
        model = ReviewAndRating
        fields = ['rating', 'review'] 
        
        widgets = {
            'review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Racontez-nous votre expérience avec ce produit...',
                'style': 'resize: none;' # Évite que l'utilisateur déforme ton UI
            }),
        }

    # Validation personnalisée pour le texte (Optionnel mais recommandé)
    def clean_review(self):
        review = self.cleaned_data.get('review')
        if len(review) < 10:
            raise forms.ValidationError("Votre avis est trop court (minimum 10 caractères).")
        return review

# Formulaire pour les images multiples (si besoin d'un formset plus tard)
class ReviewImageForm(forms.ModelForm):
    class Meta:
        model = ReviewImage
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*' # Filtre les fichiers dès l'explorateur Windows
            }),
        }