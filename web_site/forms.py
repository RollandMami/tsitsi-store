from django import forms
from django.forms import inlineformset_factory
from .models import SiteSettings, TimelineEvent, TeamMember


# 1. Le formulaire principal pour les paramètres du site
class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        # On liste absolument tous les champs modifiables
        fields = [
            'site_name', 'slogan', 'logo', 'icon', 
            'banner_title', 'banner_sub_title', 'banner_desckop', 'banner_mobile',
            'description', 'email', 'phone', 'address', 'currency',
            'since_year', 'service_summary', 'target_audience', 'main_objective',
            'mission_description', 'vision_description', 'values_text',
            'footer_about', 'footer_link_1_label', 'footer_link_1_url',
            'footer_link_2_label', 'footer_link_2_url', 'footer_link_3_label', 'footer_link_3_url',
            'facebook_url', 'instagram_url', 'linkedin_url', 'copyright_text',
            'selling_point_1_title', 'selling_point_1_description',
            'selling_point_2_title', 'selling_point_2_description',
            'selling_point_3_title', 'selling_point_3_description',
        ]
        
        # On utilise des widgets HTML pour forcer l'affichage propre des zones de texte
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'footer_about': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'values_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ex:\nTransparence totale\nInnovation constante'}),
            'mission_description': forms.Textarea(attrs={'rows': 3}),
            'vision_description': forms.Textarea(attrs={'rows': 3}),
            'banner_title': forms.Textarea(attrs={'rows': 2}),
            'banner_sub_title': forms.Textarea(attrs={'rows': 2}),
        }


# 2. Formset pour le Parcours (Timeline)
TimelineFormSet = inlineformset_factory(
    SiteSettings, 
    TimelineEvent,
    fields=['year', 'title', 'description', 'order'],
    extra=1,            # Un formulaire vide prêt pour l'ajout
    can_delete=True,    # Case à cocher pour supprimer
    widgets={
        'description': forms.Textarea(attrs={'rows': 2}),
        'year': forms.TextInput(attrs={'placeholder': 'Ex: 2023'}),
    }
)


# 3. Formset pour l'Équipe (Robustesse maximale)
TeamFormSet = inlineformset_factory(
    SiteSettings, 
    TeamMember,
    fields=['first_name', 'last_name', 'role', 'bio', 'photo', 'is_active'],
    extra=1, 
    can_delete=True,
    widgets={
        'bio': forms.Textarea(attrs={'rows': 2}),
    }
)