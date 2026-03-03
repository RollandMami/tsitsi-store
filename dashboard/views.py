from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Avg, Count, F, Q
from django.db import models
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncDay
from datetime import timedelta
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib import messages
import json
from orders.models import Order, OrderItem
from store.models import Category, Product  
from users.models import CustomUser 
from .forms import UserForm
from django.contrib.admin.views.decorators import staff_member_required
import datetime
from django.template.loader import get_template
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Image as PlImage
from django.conf import settings
import os

# --- FONCTIONS DE SÉCURITÉ ---
def is_staff_member(user):
    return user.is_active and user.is_staff
    
@login_required 
@user_passes_test(is_staff_member)
def dashboard(request):
    # --- LOGIQUE DE FILTRE PAR PÉRIODE ---
    period = request.GET.get('period', 'this_month')
    now = timezone.now()
    start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == '7days':
        start_date = now - timedelta(days=7)
    elif period == '30days':
        start_date = now - timedelta(days=30)
    elif period == 'this_year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    orders_base = Order.objects.filter(status__in=['Completed', 'Accepted', 'New'])
    orders_filtered = orders_base.filter(created__gte=start_date)

    # KPIs
    total_orders = orders_filtered.count()
    total_revenue = round(orders_filtered.aggregate(Sum('order_total'))['order_total__sum'] or 0, 2)
    average_order_value = round(orders_filtered.aggregate(Avg('order_total'))['order_total__avg'] or 0, 2)
    
    # STATS GLOBALES
    recent_orders = Order.objects.all().select_related('user').order_by('-created')[:5]
    total_products = Product.objects.filter(is_available=True).count()
    low_stock_products = Product.objects.filter(stock__lte=F('reorder_point'), is_available=True).order_by('stock')[:10]
    total_users = CustomUser.objects.filter(is_active=True, is_staff=False).count()

    # GRAPHIQUES
    # Calcul du top produits basé sur les OrderItem (plus fiable sur les relations)
    top_items_qs = OrderItem.objects.filter(
        order__created__gte=start_date,
        product__is_available=True
    ).values('product__id', 'product__product_name')\
     .annotate(total_sold=Sum('quantity'))\
     .order_by('-total_sold')[:5]

    top_labels = [item['product__product_name'] for item in top_items_qs]
    top_quantities = [int(item['total_sold']) for item in top_items_qs]
    
    if period in ['today', '7days']:
        trunc_func = TruncDay('created')
        date_format = '%d %b'
    else:
        trunc_func = TruncMonth('created')
        date_format = '%b %Y'

    sales_by_period = orders_filtered.annotate(period_label=trunc_func)\
        .values('period_label')\
        .annotate(total=Sum('order_total'), count=Count('id'))\
        .order_by('period_label')

    sales_labels = [data['period_label'].strftime(date_format) for data in sales_by_period]
    sales_data = [float(data['total']) for data in sales_by_period]
    orders_chart_data = [data['count'] for data in sales_by_period]

    context = {
        'period': period,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'average_order_value': average_order_value,
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'top_products_labels_json': json.dumps(top_labels),
        'top_products_data_json': json.dumps(top_quantities),
        'sales_labels_json': json.dumps(sales_labels),
        'sales_data_json': json.dumps(sales_data),
        'orders_data_json': json.dumps(orders_chart_data),
        'title': 'Tableau de Bord Dynamique',
    }
    return render(request, 'dashboard/main_dashboard.html', context)

# --- GESTION DES PRODUITS ---

@staff_member_required
def dashboard_products(request):
    keyword = request.GET.get('keyword', '')
    
    # Optimisation select_related pour éviter les requêtes N+1 sur les catégories
    products = Product.objects.select_related('category').all().order_by('-created_date')
    categories = Category.objects.all()
    
    if keyword:
        products = products.filter(
            Q(product_name__icontains=keyword) | 
            Q(category__name__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # FIX : On passe categories dans le render_to_string pour que le select s'affiche en AJAX
        html = render_to_string('dashboard/partials/product_table_results.html', {
            'products': products,
            'categories': categories
        })
        return JsonResponse({
            'html': html,
            'count': products.count()
        })

    context = {
        'products': products,
        'active_menu': 'products',
        'categories': categories,
        'title': 'Gestion des Produits',
    }
    return render(request, 'dashboard/products.html', context)

@require_POST
@staff_member_required
def update_product_inline(request, pk):
    try:
        product = get_object_or_404(Product, pk=pk)
        
        product.product_name = request.POST.get('product_name', product.product_name)
        product.price = request.POST.get('price', product.price)
        product.stock = request.POST.get('stock', product.stock)
        product.is_available = request.POST.get('is_available') == 'True'
        
        cat_id = request.POST.get('category')
        if cat_id:
            # Plus efficace : assignation par ID
            product.category_id = cat_id
        
        if request.FILES.get('images'):
            product.images = request.FILES.get('images')
            
        product.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
@staff_member_required
def delete_product_inline(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return JsonResponse({'status': 'success'})

@staff_member_required
def stock_dashboard(request):
    # On récupère les produits simplement pour éviter l'erreur de prefetch
    products = Product.objects.all().select_related('category')
    
    # Calculs des compteurs
    # On s'assure d'avoir 0 si le résultat est None
    total_stock_sum = products.aggregate(Sum('stock'))['stock__sum'] or 0
    out_of_stock_count = products.filter(stock__lte=0).count()
    low_stock_count = products.filter(stock__gt=0, stock__lt=5).count()
    
    context = {
        'products': products,
        'total_stock_sum': total_stock_sum,
        'out_of_stock_count': out_of_stock_count,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'dashboard/stock.html', context)

@require_POST
def update_stock_ajax(request):
    data = json.loads(request.body)
    product_id = data.get('id')
    new_stock = data.get('new_stock')
    
    try:
        product = Product.objects.get(id=product_id)
        product.stock = new_stock
        product.save()
        return JsonResponse({'success': True})
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Produit non trouvé'})
    

@staff_member_required
def order_dashboard(request):
    orders = Order.objects.all().order_by('-created')
    
    # Logique de recherche AJAX
    query = request.GET.get('q', '')
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        orders = orders.filter(
            Q(order_number__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )
        html = render_to_string('dashboard/order_list_partial.html', {'orders': orders})
        return JsonResponse({'html': html})

    # Statistiques pour KPIs
    total_orders = orders.count()
    pending_orders = orders.filter(status='New').count()
    cancelled_orders = orders.filter(status='Cancelled').count()
    daily_rev = orders.filter(status='Completed').aggregate(Sum('order_total'))['order_total__sum'] or 0

    # Données Graphique Radar pour Performance Produits (Besoin de min 3 points pour un radar)
    top_items = OrderItem.objects.filter(
        product__is_available=True
    ).values('product__product_name', 'product__id').annotate(
        total=Sum('quantity')
    ).order_by('-total')[:8]
    
    top_names = [item['product__product_name'] for item in top_items]
    top_counts = [int(item['total'] or 0) for item in top_items]
    
    # Données Réapprovisionnement - Produits en faible stock
    low_stock_products = Product.objects.filter(
        stock__lte=F('reorder_point'),
        is_available=True
    ).values(
        'id', 'product_name', 'stock', 'reorder_point', 'price'
    ).order_by('stock')[:10]

    context = {
        'orders': orders,
        'total_orders_count': total_orders,
        'orders_pending_count': pending_orders,
        'orders_cancelled_count': cancelled_orders,
        'daily_revenue': daily_rev,
        'top_product_names': top_names,
        'top_product_counts': top_counts,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'dashboard/order_dashboard.html', context)

@staff_member_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    
    valid_statuses = dict(Order._meta.get_field('status').choices).keys()
    
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        return JsonResponse({'status': 'success', 'message': f'Commande #{order.order_number} mise à jour.'}, json_dumps_params={'ensure_ascii': False})
    
    return JsonResponse({'status': 'error', 'message': 'Statut invalide.'}, status=400, json_dumps_params={'ensure_ascii': False})


@staff_member_required
def order_details(request, order_id):
    """Affiche les détails complets d'une commande."""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    # Calcul du sous-total HT
    subtotal_ht = 0
    for item in order_items:
        item_total = item.sub_total()
        subtotal_ht += float(item_total) if item_total else 0
    
    # Calcul de la TVA (20%)
    tva_rate = 0.20
    tva_amount = subtotal_ht * tva_rate
    total_ttc = subtotal_ht + tva_amount
    
    context = {
        'order': order,
        'order_items': order_items,
        'title': f'Détails de la Commande #{order.order_number}',
        'subtotal_ht': subtotal_ht,
        'tva_amount': tva_amount,
        'total_ttc': total_ttc,
    }
    return render(request, 'dashboard/order_details.html', context)


@staff_member_required
def download_order_invoice(request, order_id):
    """Télécharge la facture PDF d'une commande."""
    order = get_object_or_404(Order, id=order_id)
    return generate_invoice_pdf(request, order.order_number)


@staff_member_required
@require_POST
def delete_order(request, order_id):
    """Supprime une commande (AJAX ou POST)."""
    try:
        order = get_object_or_404(Order, id=order_id)
        order_number = order.order_number
        order.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'Commande #{order_number} supprimée.'})
        else:
            messages.success(request, f'Commande #{order_number} supprimée avec succès.')
            return redirect('dashboard:order_dashboard')
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        else:
            messages.error(request, f'Erreur: {str(e)}')
            return redirect('dashboard:order_dashboard')


def generate_invoice_pdf(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    order_items = OrderItem.objects.filter(order=order)

    # Créer la réponse HTTP avec le type PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{order_number}.pdf"'

    # Créer le canevas PDF
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # --- Header avec Logo ---
    # Chemin vers le logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'Logo.png')
    
    # Si le fichier static n'existe pas, essayer le chemin statfiles
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'Logo.png')
    
    # Afficher le logo s'il existe
    if os.path.exists(logo_path):
        try:
            p.drawImage(logo_path, 50, height - 70, width=60, height=60, preserveAspectRatio=True)
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
    
    # Afficher le titre à droite du logo
    p.setFont("Helvetica-Bold", 20)
    p.drawString(130, height - 50, "TSITSI STORE")
    
    p.setFont("Helvetica", 12)
    p.drawString(130, height - 80, f"Facture N°: {order.order_number}")
    p.drawString(130, height - 100, f"Date: {order.created.strftime('%d/%m/%Y')}")
    p.drawString(130, height - 120, f"Client: {order.full_name()}")

    # --- Tableau des produits ---
    y = height - 160
    p.line(50, y, 550, y) # Ligne de séparation
    y -= 20
    
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, "Produit")
    p.drawString(300, y, "Qté")
    p.drawString(400, y, "Prix Unit.")
    p.drawString(500, y, "Total")
    
    y -= 20
    p.setFont("Helvetica", 10)
    
    subtotal = 0
    for item in order_items:
        product_name = item.product.product_name if item.product else 'Produit supprimé'
        item_total = item.sub_total()
        subtotal += float(item_total) if item_total else 0
        
        p.drawString(50, y, product_name[:40])
        p.drawString(300, y, str(item.quantity))
        p.drawString(400, y, f"{item.product_price} Ar")
        p.drawString(500, y, f"{item.sub_total()} Ar")
        y -= 20
        if y < 100: # Nouvelle page si nécessaire
            p.showPage()
            y = height - 50

    # --- Calcul TVA et Total ---
    tva_rate = 0.20  # TVA à 20%
    tva_amount = subtotal * tva_rate
    total_ttc = subtotal + tva_amount

    # --- Total HT, TVA, TTC ---
    y -= 20
    p.line(50, y + 15, 550, y + 15)
    
    p.setFont("Helvetica", 11)
    p.drawRightString(550, y, f"Sous-Total HT: {subtotal:,.2f} Ar")
    
    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(550, y, f"TVA (20%): {tva_amount:,.2f} Ar")
    
    y -= 25
    p.line(50, y + 15, 550, y + 15)
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(550, y, f"TOTAL TTC: {total_ttc:,.2f} Ar")
    
    # --- Pied de Page (Infos Entreprise) ---
    footer_y = 50
    p.line(50, footer_y + 30, 550, footer_y + 30)
    
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, footer_y + 15, "TSITSI STORE")
    
    p.setFont("Helvetica", 9)
    p.drawString(50, footer_y, "Adresse: Antananarivo, Madagascar")
    p.drawString(300, footer_y, "Téléphone: +261 20 XX XX XX XX")
    
    footer_y -= 15
    p.drawString(50, footer_y, "Email: info@tsitsistore.mg")
    p.drawString(300, footer_y, "SIRET: XXXXXXXXXX")
    
    footer_y -= 15
    p.drawString(50, footer_y, "Merci pour votre achat!")
    p.drawString(300, footer_y, f"Généré le: {order.created.strftime('%d/%m/%Y %H:%M')}")

    p.showPage()
    p.save()
    return response


@staff_member_required
def dashboard_users(request):
    """Affiche la liste des utilisateurs (avec recherche et pagination)."""
    query = request.GET.get('q', '')
    users_qs = CustomUser.objects.all().order_by('-date_joined')

    if query:
        users_qs = users_qs.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query)
        )

    paginator = Paginator(users_qs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('dashboard/partials/user_table_results.html', {'users': page_obj})
        return JsonResponse({'html': html, 'count': users_qs.count()})

    context = {
        'users': page_obj,
        'active_menu': 'clients',
        'title': 'Gestion des Clients',
    }
    return render(request, 'dashboard/users.html', context)


@require_POST
@staff_member_required
def update_user_inline(request, pk):
    """Endpoint AJAX pour modifier uniquement l'état actif/staff depuis la table."""
    try:
        user = get_object_or_404(CustomUser, pk=pk)

        # Empêcher la désactivation/suppression de soi-même via cette route
        if user == request.user and request.POST.get('is_active') == 'False':
            return JsonResponse({'status': 'error', 'message': "Impossible de désactiver votre propre compte."}, status=400)

        is_active = request.POST.get('is_active')
        is_staff = request.POST.get('is_staff')

        if is_active is not None:
            user.is_active = (is_active == 'True')
        if is_staff is not None:
            user.is_staff = (is_staff == 'True')

        user.save()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@require_POST
@staff_member_required
def delete_user_inline(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        return JsonResponse({'status': 'error', 'message': "Impossible de supprimer votre propre compte."}, status=400)
    if user.is_superuser:
        return JsonResponse({'status': 'error', 'message': "Impossible de supprimer un superuser."}, status=400)

    user.delete()
    return JsonResponse({'status': 'success'})


@staff_member_required
def create_user(request):
    """Créer un nouvel utilisateur via le dashboard."""
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Utilisateur {user.email} créé avec succès.")
            return redirect('dashboard:clients')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserForm()

    context = {
        'form': form,
        'title': 'Créer un nouvel utilisateur',
        'page_title': 'Créer un utilisateur',
        'is_create': True,
    }
    return render(request, 'dashboard/user_form.html', context)


@staff_member_required
def edit_user(request, pk):
    """Modifier un utilisateur existant."""
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {user.email} mis à jour avec succès.")
            return redirect('dashboard:clients')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserForm(instance=user)

    context = {
        'form': form,
        'title': f'Modifier {user.email}',
        'page_title': f'Modifier {user.email}',
        'is_create': False,
    }
    return render(request, 'dashboard/user_form.html', context)