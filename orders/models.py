from decimal import Decimal

from django.db import models
from django.conf import settings
from store.models import Product # Importe le modèle Product

# --- Modèle 1 : Order (La Commande) ---
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='orders',
        null=True, 
        blank=True,
        verbose_name="Utilisateur"
    )
    
    # Informations Client
    first_name = models.CharField(max_length=100, verbose_name="Prénom")
    last_name = models.CharField(max_length=100, verbose_name="Nom")
    email = models.EmailField(max_length=100, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Téléphone")
    
    # Livraison (Augmentation de la taille des champs)
    address_line_1 = models.CharField(max_length=255, verbose_name="Adresse Ligne 1")
    address_line_2 = models.CharField(max_length=255, blank=True, verbose_name="Adresse Ligne 2 (Optionnel)")
    city = models.CharField(max_length=100, verbose_name="Ville")
    state = models.CharField(max_length=100, verbose_name="État/Province")
    country = models.CharField(max_length=100, verbose_name="Pays")
    
    # Détails Commande
    order_number = models.CharField(max_length=30, unique=True, blank=True, verbose_name="Numéro de Commande")
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Frais de port") # AJOUTÉ
    order_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name="Total Commande")
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Taxes")
    
    paid = models.BooleanField(default=False, verbose_name="Payée") 
    status = models.CharField(
        max_length=10, 
        choices=[
            ('New', 'Nouvelle'), 
            ('Accepted', 'Acceptée'), 
            ('Completed', 'Terminée'), 
            ('Cancelled', 'Annulée')
        ],
        default='New',
        verbose_name="Statut"
    )
    
    created = models.DateTimeField(auto_now_add=True, verbose_name="Date de Création")
    updated = models.DateTimeField(auto_now=True, verbose_name="Dernière Mise à Jour")
    ip = models.CharField(max_length=45, blank=True, verbose_name="Adresse IP") # IPv6 peut faire 45 caractères

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ('-created',)

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.order_number or f'ID: {self.id}'

    @property
    def get_subtotal_ht(self):
        """Calcule le sous-total HT à partir des OrderProducts associés"""
        # Utilise orderproduct_set (le related_name par défaut de ton modèle OrderProduct)
        return sum(item.product_price * item.quantity for item in self.items.all())

    @property
    def get_tva(self):
        """Calcule la TVA (20%)"""
        return (self.get_subtotal_ht * Decimal('0.20')).quantize(Decimal('0.01'))

    @property
    def get_total_ttc(self):
        """Calcule le total final"""
        return self.get_subtotal_ht + self.get_tva + self.shipping_cost
    
# --- Modèle 2 : OrderItem (Article d'une Commande) ---
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items', 
        verbose_name="Commande"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="Produit"
    )
    quantity = models.IntegerField(verbose_name="Quantité")
    product_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire payé")
    
    # AJOUT DU CHAMP SIZE (pour corriger l'erreur actuelle)
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Taille")
    
    # On garde variant pour ne rien supprimer
    variant = models.CharField(max_length=100, blank=True, verbose_name="Variante") 

    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Article de Commande'
        verbose_name_plural = 'Articles de Commande'

    def __str__(self):
        return self.product.product_name if self.product else f'Deleted Product ({self.quantity} x {self.product_price}MGA)'

    def sub_total(self):
        """Calcul pour l'affichage ligne par ligne (utilisé par l'admin et les templates)"""
        if self.product_price is not None and self.quantity is not None:
            return self.product_price * self.quantity
        return 0
    
    # Optionnel : pour avoir un joli titre dans l'admin
    sub_total.short_description = "Sous-total"
    # Dans models.py, classe Order
    @property
    def get_subtotal_ht(self):
        """Calcule le sous-total HT en utilisant le related_name 'items'"""
        # On utilise .items car c'est le nom défini dans OrderItem
        return sum(item.product_price * item.quantity for item in self.items.all())

    @property
    def get_tva(self):
        """Calcule la TVA (20%)"""
        from decimal import Decimal
        return (self.get_subtotal_ht * Decimal('0.20')).quantize(Decimal('0.01'))

    @property
    def get_total_ttc(self):
        """Calcule le total final avec shipping_cost"""
        shipping = self.shipping_cost if self.shipping_cost else 0
        return self.get_subtotal_ht + self.get_tva + shipping