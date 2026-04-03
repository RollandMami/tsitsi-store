from .models import SiteSettings

def site_settings(request):
    return {'site_config': SiteSettings.get_settings()}