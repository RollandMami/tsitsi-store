from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from django.db.models import Avg, Min, Max

# Import pour le redimensionnement automatique
from django_resized import ResizedImageField

class Category(models.Model):
    """Modele pour les catégories de produits."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom de la Categorie")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Categories'
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def get_url(self):
        return reverse('store:products_by_category', args=[self.slug])

class Product(models.Model):
    """Modele : chaque article est un noeud complet, lié par group_id."""
    category = models.ForeignKey('Category', on_delete=models.CASCADE, verbose_name='Catégorie', related_name='products')
    product_name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True, verbose_name="Description Détaillée")
    
    # Chaque article a son propre prix et son propre stock
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix (MGA)")
    stock = models.IntegerField(verbose_name="Stock disponible")
    
    images = ResizedImageField(
        size=[800, 800], 
        quality=75, 
        crop=['middle', 'center'],
        upload_to='photos/products', 
        force_format='JPEG',
        verbose_name="Image Principale"
    )
    
    # --- LOGIQUE DE GROUPE (Noeuds équivalents) ---
    group_id = models.CharField(
        max_length=50, blank=True, null=True, 
        help_text="ID commun pour lier les variantes (ex: 'CUTTER-001')."
    )
    variant_label = models.CharField(
        max_length=100, blank=True, 
        help_text="Ex: 'Rouge', 'Bleu', 'XL'."
    )
    is_main_representative = models.BooleanField(
        default=False, 
        verbose_name="Afficher en priorité dans le catalogue"
    )
    
    is_available = models.BooleanField(default=True, verbose_name="Disponible à la vente")
    reorder_point = models.IntegerField(default=5, verbose_name="Seuil Critique")
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
        ordering = ('-created_date',)

    def __str__(self):
        if self.variant_label:
            return f"{self.product_name} ({self.variant_label})"
        return self.product_name

    def get_display_price(self):
        """Calcule la fourchette de prix basée sur les membres disponibles."""
        if self.group_id:
            family_prices = Product.objects.filter(
                group_id=self.group_id, 
                is_available=True # On garde ceci pour le prix affiché en boutique
            ).aggregate(min_p=Min('price'), max_p=Max('price'))
            
            min_p = family_prices['min_p']
            max_p = family_prices['max_p']

            if min_p is not None and max_p is not None:
                if min_p == max_p:
                    return f"{int(min_p)} MGA"
                return f"{int(min_p)} - {int(max_p)} MGA"
        
        # Si aucune variante n'est dispo ou pas de group_id, on affiche le prix de l'objet lui-même
        return f"{int(self.price)} MGA"

    def get_family(self):
        """Récupère tous les membres de la famille, même ceux hors stock."""
        if not self.group_id:
            return Product.objects.filter(id=self.id)
        # On retire is_available=True pour ne pas casser l'affichage des variantes
        return Product.objects.filter(group_id=self.group_id).order_by('price')

    def get_url(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])

    def get_average_rating(self):
        # Utilise le related_name par défaut reviewandrating_set
        return self.reviewandrating_set.filter(is_active=True).aggregate(average=Avg('rating'))['average'] or 0

class ProductImage(models.Model):
    """Galerie d'images additionnelles pour le produit."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = ResizedImageField(
        size=[800, 800], 
        quality=75, 
        upload_to='photos/product_gallery',
        force_format='JPEG',
        verbose_name="Image Additionnelle"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Image de la Galerie'
        verbose_name_plural = 'Images de la Galerie'


class ReviewAndRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    rating = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(7)])
    review = models.TextField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Avis et Note"
        verbose_name_plural = "Avis et Notes"
        unique_together = ('user', 'product') 
    
    def __str__(self):
        return f"{self.rating} étoiles pour {self.product.product_name}"


class ReviewImage(models.Model):
    review = models.ForeignKey(ReviewAndRating, on_delete=models.CASCADE, related_name='images')
    image = ResizedImageField(
        size=[600, 600], 
        quality=70, 
        upload_to='photos/reviews/%Y/%m/%d/',
        force_format='JPEG',
        verbose_name="Image jointe"
    )
    
    class Meta:
        verbose_name = "Image d'Avis"
        verbose_name_plural = "Images d'Avis"