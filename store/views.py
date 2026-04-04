import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import F, Q, Count, Sum
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from web_site.models import SiteSettings

# Local apps imports
from .models import Product, Category, ProductImage, ReviewAndRating
from .forms import ReviewForm, ReviewImageForm

# --- HELPERS ---
def is_superuser_or_staff(user):
    return user.is_active and (user.is_superuser or user.is_staff)

# --- 0. ACCUEIL ---
def home(request):
    #On récupère l'instance unique des configurations du site
    site_config = SiteSettings.get_settings()

    # On affiche uniquement les représentants principaux pour éviter les doublons
    products = Product.objects.filter( 
        is_main_representative=True
    ).order_by('-created_date')[:8]
    
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'site_config': site_config,
        'title': 'Acceuil' if site_config.site_name else 'Bienvenue chez E-commerce',
    }
    return render(request, 'store/home.html', context)

# --- 1. GESTION DES STOCKS & AJAX ---
@user_passes_test(is_superuser_or_staff)
def low_stock_report(request):
    """
    Rapport basé uniquement sur Product (car les variantes sont des Products).
    Affiche tout article dont le stock est <= 5 (ou ton reorder_point personnalisé).
    """
    low_stock_products = Product.objects.filter(
        stock__lte=5, # Tu peux remettre F('reorder_point') si tu l'as gardé
        is_available=True
    ).select_related('category').order_by('stock')

    context = { 
        'low_stock_products': low_stock_products,
        'title': 'Rapport de Stock Critique'
    }
    return render(request, 'store/low_stock_report.html', context)

@user_passes_test(is_superuser_or_staff)
def update_stock_ajax(request):
    """
    La fonction manquante qui causait l'AttributeError.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_id = data.get('id')
            new_stock = data.get('new_stock')
            
            product = get_object_or_404(Product, id=product_id)
            product.stock = new_stock
            product.save()
            
            return JsonResponse({'success': True, 'new_stock': product.stock})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# --- 2. CATALOGUE ---
def products_list_view(request, category_slug=None):
    categories = Category.objects.all()
    sort = request.GET.get('sort')
    
    # FILTRE CRITIQUE : On ne prend que les 'is_main_representative' 
    # pour ne pas voir 5 fois le même carnet de couleurs différentes.
    all_available = Product.objects.filter(
        is_main_representative=True
    ).select_related('category')
    
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = all_available.filter(category=current_category)
        title = current_category.name
    else:
        products = all_available
        current_category = None
        title = "Tous les Produits"

    # Tri
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_date')
    
    paginator = Paginator(products, 12) 
    page_obj = paginator.get_page(request.GET.get('page'))
    
    context = {
        'title': title,
        'current_category': current_category,
        'categories': categories,
        'page_obj': page_obj,
        'products_count': products.count(),
    }
    return render(request, 'store/catalogue.html', context)

# --- 3. DÉTAIL PRODUIT ---
def product_detail_view(request, category_slug, product_slug):
    # 1. On récupère le produit spécifique demandé
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    
    # 2. On récupère toute la famille via le group_id, en excluant le produit actuel
    # Si group_id est None ou vide, c'est un produit unique et il n'a pas de variantes.
    if product.group_id:
        variants = Product.objects.filter(
            group_id=product.group_id
        ).exclude(id=product.id).order_by('price') # Optionnel : trier par prix croissant
    else:
        variants = Product.objects.none()

    product_gallery = product.gallery.all()
    reviews = ReviewAndRating.objects.filter(product=product, is_active=True).order_by('-created_at')
    
    context = {
        'product': product,
        'variants': variants, 
        'product_gallery': product_gallery,
        'reviews': reviews,
        'review_form': ReviewForm(),
        'similar_products': Product.objects.filter(
            category=product.category,
            is_main_representative=True
        ).exclude(group_id=product.group_id)[:4],
    }
    return render(request, 'store/product_detail.html', context)

# --- 4. RECHERCHE ---
def search(request):
    keyword = request.GET.get('keyword', '')
    # Dans la recherche, on peut autoriser l'affichage de tous les variants 
    # ou rester sur les représentants. Ici, on reste sur les représentants pour la clarté.
    products = Product.objects.filter(is_available=True, is_main_representative=True)
    if keyword:
        products = products.filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
    
    context = {
        'products': products,
        'products_count': products.count(),
        'keyword': keyword,
    }
    return render(request, 'store/search_results.html', context)

# --- 5. AVIS ---
@login_required
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewAndRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Merci ! Votre avis a été mis à jour.')
            else:
                print(form.errors)
            return redirect(url)
        except ReviewAndRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Avis publié.')
            else:
                print(form.errors)
            return redirect(url)
    return redirect(url)

def category_list_view(request):
    """
    Affiche la liste des catégories avec le compte des produits.
    """
    # On utilise 'products' car c'est le related_name dans le modèle Product
    categories = Category.objects.all().annotate(
        product_count=Count(
            'products', 
            filter=Q(products__is_available=True)
        )
    )
    
    context = {
        'categories': categories,
        'title': 'Nos Rayons',
    }
    return render(request, 'store/category_list_view.html', context)