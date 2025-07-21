from django.contrib import admin
from django.urls import path
from pages import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('<slug:slug>/', views.render_page, name='render_page'),
]

# Add static and media URL patterns for development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.name = "AI CMS"
admin.site.site_header = "AI CMS"