from django.contrib import admin
from .models import SiteSettings, Team, TeamMember


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'mission']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'role', 'team', 'is_active']
    list_filter = ['team', 'is_active']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'slogan', 'email', 'phone']
    fieldsets = (
        ('Information principale', {
            'fields': ('site_name', 'slogan', 'logo', 'description', 'currency')
        }),
        ('Contact et localisation', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Footer', {
            'fields': (
                'footer_about',
                'footer_link_1_label', 'footer_link_1_url',
                'footer_link_2_label', 'footer_link_2_url',
                'footer_link_3_label', 'footer_link_3_url',
                'facebook_url', 'instagram_url', 'linkedin_url',
                'copyright_text',
            )
        }),
        ('Arguments de vente', {
            'fields': (
                'selling_point_1_title', 'selling_point_1_description',
                'selling_point_2_title', 'selling_point_2_description',
                'selling_point_3_title', 'selling_point_3_description',
            )
        }),
        ('Équipe', {
            'fields': ('team',)
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
