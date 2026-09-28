from django.contrib import admin

from .models import Presence


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'classe', 'date', 'statut', 'justifie', 'motif')
    list_filter = ('date', 'statut', 'justifie', 'classe')
    search_fields = ('eleve__nom', 'eleve__prenom')
    autocomplete_fields = ('eleve', 'classe')