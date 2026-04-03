from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='main_dashboard'),
    path('stock/', views.stock_dashboard, name='stock'),
    path('products/', views.dashboard_products, name='products'),
    path('products/update/<int:pk>/', views.update_product_inline, name='update_product_inline'),
    path('products/delete/<int:pk>/', views.delete_product_inline, name='delete_product_inline'),
    path('update-stock-ajax/', views.update_stock_ajax, name='update_stock_ajax'),
    path('orders/', views.order_dashboard, name='order_dashboard'),
    path('orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/details/', views.order_details, name='order_details'),
    path('orders/<int:order_id>/invoice/', views.download_order_invoice, name='download_order_invoice'),
    path('orders/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    path('clients/', views.dashboard_users, name='clients'),
    path('clients/create/', views.create_user, name='create_user'),
    path('clients/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('clients/update/<int:pk>/', views.update_user_inline, name='update_user_inline'),
    path('clients/delete/<int:pk>/', views.delete_user_inline, name='delete_user_inline'),
	path('settings/', views.edit_site_settings, name='edit_site_settings'),
]