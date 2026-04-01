import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, F, Q, Case, When, IntegerField, Count
from django.contrib import messages
from django.template.loader import render_to_string

# Imports des modèles locaux
from store.models import Product, Category
from orders.models import Order, OrderItem
from users.models import CustomUser

# --- SÉCURITÉ ---
def is_admin(user):
    return user.is_active and (user.is_superuser or user.is_staff)


# ==========================================
# 1. ACCUEIL DU DASHBOARD (STATISTIQUES)
# ==========================================

@user_passes_test(is_admin)
def dashboard(request):
    """ Vue principale avec les KPIs généraux """
    orders = Order.objects.all()
    products = Product.objects.all()
    users = CustomUser.objects.all()

    total_revenue = orders.filter(paid=True).aggregate(Sum('order_total'))['order_total__sum'] or 0
    context = {
        'total_orders': orders.count(),
        'total_revenue': total_revenue,
        'total_products': products.count(),
        'total_customers': users.filter(is_staff=False).count(),
        'recent_orders': orders.order_by('-created')[:5],
        'title': 'Tableau de Bord'
    }
    return render(request, 'dashboard/main_dashboard.html', context)

# ==========================================
# 2. TABLEAU DE BORD - STOCKS & PRODUITS
# ==========================================

@user_passes_test(is_admin)
def stock_dashboard(request):
    """ 
    Vue des KPIs simplifiée : chaque produit est désormais un nœud autonome.
    On calcule le stock global en sommant simplement le champ 'stock' de tous les articles.
    """
    # On récupère tous les articles (indépendamment de leur group_id)
    products = Product.objects.all().select_related('category').order_by('product_name')

    # Calcul des KPIs via agrégation (plus rapide qu'une boucle for)
    stats = products.aggregate(
        total_sum=Sum('stock'),
        out_of_stock=Count('id', filter=Q(stock__lte=0)),
        low_stock=Count('id', filter=Q(stock__gt=0, stock__lt=5))
    )

    # Pour garder la compatibilité avec ton template qui utilise 'product.effective_stock'
    for product in products:
        product.effective_stock = product.stock

    context = {
        'products': products,
        'total_stock_sum': stats['total_sum'] or 0,
        'out_of_stock_count': stats['out_of_stock'] or 0,
        'low_stock_count': stats['low_stock'] or 0,
        'title': 'État des Stocks (Nœuds Autonomes)'
    }
    return render(request, 'dashboard/stock.html', context)

@user_passes_test(is_admin)
def dashboard_products(request):
    """ Liste des produits avec recherche AJAX """
    query = request.GET.get('q', '')
    categories = Category.objects.all()
    products = Product.objects.all().select_related('category').order_by('-created_date')
    
    if query:
        products = products.filter(Q(product_name__icontains=query) | Q(category__name__icontains=query))
    context = {
        'products': products,
        'categories': categories,
        'title': 'Gestion Produits'
    }
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('dashboard/partials/product_table_results.html', context)
        return JsonResponse({'html': html, 'count': products.count()})
        
    return render(request, 'dashboard/products.html', context)

@user_passes_test(is_admin)
def update_stock_ajax(request):
    """ Mise à jour rapide du stock via Modal """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = get_object_or_404(Product, id=data.get('id'))
            product.stock = data.get('new_stock')
            product.save()
            return JsonResponse({'success': True, 'new_stock': product.stock})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=400)

@user_passes_test(is_admin)
def update_product_inline(request, pk):
    """ Modification rapide d'un produit (Prix/Dispo) """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.price = request.POST.get('price')
        product.is_available = 'is_available' in request.POST
        product.save()
        messages.success(request, f"Produit {product.product_name} mis à jour.")
    return redirect('dashboard:dashboard_products')

@user_passes_test(is_admin)
def delete_product_inline(request, pk):
    """ Suppression d'un produit """
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('dashboard:dashboard_products')

# ==========================================
# 3. GESTION DES COMMANDES (Orders)
# ==========================================

@user_passes_test(is_admin)
def order_dashboard(request):
    """ Liste et suivi des commandes """
    orders = Order.objects.all().order_by('-created')
    context = {
        'orders': orders,
        'pending_count': orders.filter(status='New').count(),
        'total_revenue': orders.filter(paid=True).aggregate(Sum('order_total'))['order_total__sum'] or 0
    }
    return render(request, 'dashboard/order_dashboard.html', context)


@user_passes_test(is_admin)
def update_order_status(request, order_id):
    """ Change le statut (New, Accepted, Completed, Cancelled) """
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.status = request.POST.get('status')
        order.save()
        # Si la requête vient de Fetch (AJAX)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f"Statut de la commande #{order.order_number} mis à jour en '{order.status}'."
            })
        
        # Si c'est un formulaire classique (sans JS)
        messages.success(request, f"Statut commande #{order.order_number} mis à jour.")
        return redirect('dashboard:order_dashboard')
    
@user_passes_test(is_admin)
def download_order_invoice(request, order_id):
    """ Génération simple de facture (PDF ou HTML) """
    order = get_object_or_404(Order, id=order_id)
    order_products = OrderItem.objects.filter(order=order)
    context = {'order': order, 'order_products': order_products}
    return render(request, 'dashboard/invoice_pdf_template.html', context)

@user_passes_test(is_admin)
def order_details(request, order_id):
    """ Vue détaillée d'une commande spécifique """
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    subtotal = order_items.aggregate(total=Sum(F('product_price') * F('quantity')))['total'] or 0
    
    context = {
        'order': order,
        'order_items': order_items,
        'subtotal': subtotal,
    }
    return render(request, 'dashboard/order_details.html', context)

@user_passes_test(is_admin)
def delete_order(request, order_id):
    """ Supprimer une commande """
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.warning(request, "Commande supprimée.")
    return redirect('dashboard:order_dashboard')

# ==========================================
# 4. GESTION DES UTILISATEURS (Accounts)
# ==========================================

@user_passes_test(is_admin)
def dashboard_users(request):
    """ Gestion des clients et membres du staff """
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/users.html', {'users': users})

@user_passes_test(is_admin)
def create_user(request):
    """ Création manuelle d'un compte """
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.create_user(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=email,
            username=email.split('@')[0],
            password="TemporaryPassword123!" 
        )
        messages.success(request, f"Compte créé pour {email}.")
        return redirect('dashboard:dashboard_users')
    return render(request, 'dashboard/user_form.html')

@user_passes_test(is_admin)
def edit_user(request, pk):
    """ Editer les permissions ou infos d'un user """
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.is_active = 'is_active' in request.POST
        user.is_staff = 'is_staff' in request.POST
        user.save()
        messages.info(request, "Modifications enregistrées.")
        return redirect('dashboard:dashboard_users')
    return render(request, 'dashboard/user_form.html', {'user_edit': user})

@user_passes_test(is_admin)
def update_user_inline(request, pk):
    """ Mise à jour rapide des rôles utilisateur """
    user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        user.is_staff = 'is_staff' in request.POST
        user.is_active = 'is_active' in request.POST
        user.save()
        messages.success(request, f"Permissions de {user.email} mises à jour.")
    return redirect('dashboard:dashboard_users')

@user_passes_test(is_admin)
def delete_user_inline(request, pk):
    """ Suppression d'un compte via AJAX """
    user = get_object_or_404(CustomUser, pk=pk)
    user.delete()
    return JsonResponse({'success': True})