from django import forms
from django.forms import inlineformset_factory
from .models import SiteSettings, TimelineEvent, TeamMember


# 1. Le formulaire principal pour les paramètres du site
class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        # On liste tous les champs modifiables (Exclut l'équipe globale liée pour l'instant)
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
        
        # On utilise des widgets pour forcer l'affichage de textareas au lieu de simples inputs
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'footer_about': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'values_text': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Transparence totale\nInnovation constante\nOrientation Client'}),
            'banner_title': forms.Textarea(attrs={'rows': 2}),
            'banner_sub_title': forms.Textarea(attrs={'rows': 2}),
        }


# 2. Formset pour le Parcours (Timeline)
# Permet d'ajouter/modifier/supprimer plusieurs étapes à la fois
TimelineFormSet = inlineformset_factory(
    SiteSettings, 
    TimelineEvent,
    fields=['year', 'title', 'description', 'order'],
    extra=1,            # Nombre de formulaires vides à afficher pour les ajouts
    can_delete=True,    # Permet de cocher une case pour supprimer l'étape
    widgets={
        'description': forms.Textarea(attrs={'rows': 2}),
        'year': forms.TextInput(attrs={'placeholder': 'Ex: 2023'}),
    }
)


# 3. Formset pour l'Équipe
# Permet d'ajouter/modifier/supprimer les collaborateurs
TeamMemberFormSet = inlineformset_factory(
    SiteSettings,
    # Attention : Ton modèle TeamMember actuel est lié à "Team" et non directement à "SiteSettings".
    # Pour que l'inlineformset marche directement depuis la page de config du site,
    # il faudrait soit lier TeamMember directement à SiteSettings, soit gérer Team séparément.
    # On va utiliser une astuce dans la vue ou adapter si besoin. 
    # Pour l'instant, on l'associe à l'instance de Team que possède SiteSettings.
)