from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from sales import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sales/', include('sales.urls')),
    path('common/', include('common.urls')),
    path('', views.index, name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

