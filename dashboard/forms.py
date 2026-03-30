from django import forms
from users.models import CustomUser
from django.core.exceptions import ValidationError

class UserForm(forms.ModelForm):
    """Formulaire optimisé pour la gestion des utilisateurs via le dashboard."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nouveau mot de passe'}),
        required=False,
        help_text="Laissez vide pour conserver le mot de passe actuel."
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}),
        required=False,
        label="Confirmer le mot de passe"
    )

    class Meta:
        model = CustomUser
        # On exclut 'password' des fields Meta car on le gère manuellement au-dessus
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+261 xx xx xxx xx'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_email(self):
        """Vérifie l'unicité de l'email (très important pour le dashboard)."""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Cet email est déjà utilisé par un autre compte.")
        return email

    def clean(self):
        """Validation croisée des mots de passe."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        # Si l'un des champs est rempli, l'autre doit l'être aussi
        if (password or password_confirm) and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
        
        return cleaned_data

    def save(self, commit=True):
        """Sauvegarde sécurisée du mot de passe avec set_password."""
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        return user