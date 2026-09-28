"""Configuration des URLs du projet."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('comptes/', include('apps.accounts.urls')),
    path('scolarite/', include('apps.scolarite.urls')),
    path('enseignants/', include('apps.enseignants.urls')),
    path('eleves/', include('apps.eleves.urls')),
    path('notes/', include('apps.notes.urls')),
    path('presences/', include('apps.presences.urls')),
    path('finance/', include('apps.finance.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])