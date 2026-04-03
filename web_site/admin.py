from django.contrib import admin
from .models import SiteSettings, TeamMember, TimelineEvent


# --- INLINES ---
# Permet de gérer la timeline directement dans la page du Site
class TimelineEventInline(admin.StackedInline):
    model = TimelineEvent
    extra = 1
    ordering = ['order', 'year']


# Permet de gérer les collaborateurs directement dans la page du Site
class TeamMemberInline(admin.StackedInline):
    model = TeamMember
    extra = 1


# --- CONFIGURATIONS ADMIN ---

@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ['year', 'title', 'order']
    list_editable = ['order'] # Pratique pour changer l'ordre directement dans la liste !


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'role', 'is_active']
    list_filter = ['is_active'] # On a retiré le filtre 'team' qui n'existe plus


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'slogan', 'email', 'phone']
    
    # On ajoute nos inlines ici pour afficher le parcours et l'équipe en bas de page
    inlines = [TimelineEventInline, TeamMemberInline]
    
    fieldsets = (
        ('Identité de base', {
            'fields': ('site_name', 'slogan', 'logo', 'icon', 'description', 'currency')
        }),
        ('Configuration des Bannières', {
            'fields': ('banner_title', 'banner_sub_title', 'banner_desckop', 'banner_mobile')
        }),
        ('Ligne de présentation (Phrase à trous)', {
            'fields': ('since_year', 'service_summary', 'target_audience', 'main_objective'),
            'description': "Ces éléments servent à remplir dynamiquement le paragraphe de présentation de l'image 1."
        }),
        ('Mission & Vision', {
            'fields': ('mission_description', 'vision_description', 'values_text'),
            'description': "Utilisez le champ 'Nos Valeurs' en revenant à la ligne pour chaque nouvelle valeur."
        }),
        ('Contact et localisation', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Arguments de vente', {
            'fields': (
                'selling_point_1_title', 'selling_point_1_description',
                'selling_point_2_title', 'selling_point_2_description',
                'selling_point_3_title', 'selling_point_3_description',
            )
        }),
        ('Pied de page & Réseaux', {
            'fields': (
                'footer_about',
                'footer_link_1_label', 'footer_link_1_url',
                'footer_link_2_label', 'footer_link_2_url',
                'footer_link_3_label', 'footer_link_3_url',
                'facebook_url', 'instagram_url', 'linkedin_url',
                'copyright_text',
            )
        }),
    )

    # Garde-fou pour n'avoir qu'une seule instance de configuration
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False