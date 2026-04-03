from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, default='Équipe Principale')
    mission = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Équipe'
        verbose_name_plural = 'Équipes'

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name='members', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Collaborateur'
        verbose_name_plural = 'Collaborateurs'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SiteSettings(models.Model):
    # Identité de base
    site_name = models.CharField(max_length=100, default='Mon Site E-commerce')
    slogan = models.CharField(max_length=200, blank=True, null=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    icon = models.ImageField(upload_to='site/', blank=True, null=True)
    
    # Textes Banner
    banner_title = models.TextField(blank=True, null=True, default='Titre banner')
    banner_sub_title = models.TextField(blank=True, null=True, default='Sous-titre banner')
    banner_desckop = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Photo de bannière Desktop")
    banner_mobile = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name="Photo de bannière Mobile")

    description = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=10, default='EUR')

    # IMAGE 1 : Données dynamiques de la phrase à trous
    since_year = models.CharField(max_length=4, blank=True, null=True, verbose_name="Année de début")
    service_summary = models.CharField(max_length=255, blank=True, null=True, verbose_name="Résumé du service/produit")
    target_audience = models.CharField(max_length=255, blank=True, null=True, verbose_name="Public cible")
    main_objective = models.CharField(max_length=255, blank=True, null=True, verbose_name="Leur objectif")

    # IMAGE 2 : Mission, Vision, Valeurs
    mission_description = models.TextField(blank=True, null=True, verbose_name="Description de la Mission")
    vision_description = models.TextField(blank=True, null=True, verbose_name="Description de la Vision")
    values_text = models.TextField(blank=True, null=True, verbose_name="Nos Valeurs", help_text="Séparez les valeurs par un retour à la ligne.")

    # Footer
    footer_about = models.TextField(blank=True, null=True)
    footer_link_1_label = models.CharField(max_length=50, blank=True, null=True)
    footer_link_1_url = models.CharField(max_length=200, blank=True, null=True)
    footer_link_2_label = models.CharField(max_length=50, blank=True, null=True)
    footer_link_2_url = models.CharField(max_length=200, blank=True, null=True)
    footer_link_3_label = models.CharField(max_length=50, blank=True, null=True)
    footer_link_3_url = models.CharField(max_length=200, blank=True, null=True)
    
    facebook_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    copyright_text = models.CharField(max_length=200, blank=True, null=True)
    
    team = models.ForeignKey(Team, related_name='site_settings', on_delete=models.SET_NULL, blank=True, null=True)

    # Trois arguments de vente
    selling_point_1_title = models.CharField(max_length=100, blank=True, null=True)
    selling_point_1_description = models.CharField(max_length=255, blank=True, null=True)
    selling_point_2_title = models.CharField(max_length=100, blank=True, null=True)
    selling_point_2_description = models.CharField(max_length=255, blank=True, null=True)
    selling_point_3_title = models.CharField(max_length=100, blank=True, null=True)
    selling_point_3_description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Paramètres du Site'
        verbose_name_plural = 'Paramètres du Site'

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings

    # Petite fonction utilitaire pour transformer le texte des valeurs en liste dans le template
    def get_values_list(self):
        if self.values_text:
            return [v.strip() for v in self.values_text.split('\n') if v.strip()]
        return []


# IMAGE 3 : Nouveau modèle pour le parcours (Timeline)
class TimelineEvent(models.Model):
    site_settings = models.ForeignKey(SiteSettings, related_name='events', on_delete=models.CASCADE)
    year = models.CharField(max_length=4, verbose_name="Année")
    title = models.CharField(max_length=150, verbose_name="Titre de l'étape")
    description = models.TextField(verbose_name="Description de l'événement")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")

    class Meta:
        verbose_name = 'Étape du parcours'
        verbose_name_plural = 'Étapes du parcours'
        ordering = ['order', 'year']

    def __str__(self):
        return f"{self.year} - {self.title}"