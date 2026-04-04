from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ReviewAndRating, ReviewImage

# --- UTILS ---
def image_preview_helper(url):
    """Génère un aperçu miniature générique."""
    return format_html('<img src="{}" style="width: 45px; height:45px; object-fit:contain; border-radius:4px; border:1px solid #eee;" />', url)

# --- INLINES ---

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ('image', 'preview')
    readonly_fields = ('preview',)
    extra = 1

    def preview(self, obj):
        if obj.image:
            return image_preview_helper(obj.image.url)
        return "-"
    preview.short_description = "Aperçu"

class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 1
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        return image_preview_helper(obj)

# --- ADMIN CLASSES ---

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'nb_produits')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def nb_produits(self, obj):
        return obj.products.count()
    nb_produits.short_description = "Nombre d'articles"
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # --- CONFIGURATION DE LA LISTE ---
    list_display = (
        'thumbnail', 
        'product_name', 
        'variant_label', # Très important pour distinguer les noeuds
        'category', 
        'price_formatted', 
        'colored_stock', 
        'is_main_representative', # Pour voir qui est le "chef" de file
        'is_available'
    )
    list_display_links = ('thumbnail', 'product_name')
    list_editable = ('is_available', 'is_main_representative', 'variant_label') 
    
    # On ajoute le filtre par group_id pour retrouver facilement une famille
    list_filter = ('category', 'is_available', 'is_main_representative', 'group_id')
    search_fields = ('product_name', 'slug', 'group_id', 'variant_label')
    inlines = [ProductImageInline]
    prepopulated_fields = {'slug': ('product_name', 'variant_label')} # Le slug doit être unique par variant
    
    save_on_top = True 

    # --- CONFIGURATION DU FORMULAIRE ---
    fieldsets = (
        ('Identité de l\'article', {
            'fields': (
                ('product_name', 'variant_label'), 
                'slug', 
                'category', 
                'description', 
                'images'
            ),
        }),
        ('Logique de Famille (Variantes)', {
            'description': "Articles liés par le même ID de groupe.",
            'fields': (('group_id', 'is_main_representative'),),
        }),
        ('Prix & Stock', {
            'fields': (('price', 'stock'), 'is_available'),
        }),
    )

    # --- MÉTHODES D'AFFICHAGE ---

    def thumbnail(self, obj):
        if obj.images:
            return image_preview_helper(obj.images.url)
        return "Pas d'image"
    thumbnail.short_description = 'Photo'

    def price_formatted(self, obj):
        return format_html('<span style="font-weight:bold;">{:,.0f} {{site_config.currency}}</span>'.format(obj.price).replace(',', ' '))
    price_formatted.short_description = 'Prix'

    def colored_stock(self, obj):
        # On peut fixer un seuil arbitraire ou garder un champ reorder_point si tu l'as laissé
        threshold = 5 
        color = "green" if obj.stock > threshold else "red"
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.stock)
    colored_stock.short_description = 'Stock'
    
@admin.register(ReviewAndRating)
class ReviewAndRatingAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'stars', 'is_active', 'created_at')
    list_filter = ('rating', 'is_active')
    readonly_fields = ('user', 'product', 'rating', 'review')# Empêche la modification des avis clients par l'admin
    inlines = [ReviewImageInline]
    actions = ['approve_reviews', 'disapprove_reviews']

    def stars(self, obj):
        return "★" * obj.rating + "☆" * (7 - obj.rating)
    stars.short_description = "Note"

    def approve_reviews(self, request, queryset):
        queryset.update(is_active=True)
    approve_reviews.short_description = "Approuver les avis sélectionnés"

    def disapprove_reviews(self, request, queryset):
        queryset.update(is_active=False)
    disapprove_reviews.short_description = "Masquer les avis sélectionnés"