from django.urls import path

from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:product_id>/', views.detail, name='detail'),
    path('product/create', views.product_create, name='product_create'),
    path('product/modify/<int:product_id>/', views.product_modify, name='product_modify'),
    path('product/delete/<int:product_id>/', views.product_delete, name='product_delete'),
]