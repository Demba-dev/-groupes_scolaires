from django.contrib import admin

from .models import Enseignant


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'sexe', 'telephone', 'user', 'actif')
    list_filter = ('sexe', 'actif')
    search_fields = ('matricule', 'nom', 'prenom', 'telephone')
    raw_id_fields = ('user',)