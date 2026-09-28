from django.contrib import admin

from .models import Frais, Paiement


@admin.register(Frais)
class FraisAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'montant', 'annee_scolaire', 'obligatoire')
    list_filter = ('annee_scolaire', 'obligatoire')
    search_fields = ('libelle',)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('recu_numero', 'eleve', 'annee_scolaire', 'frais', 'libelle', 'montant', 'mode', 'date')
    list_filter = ('annee_scolaire', 'mode', 'date')
    search_fields = ('eleve__nom', 'eleve__prenom', 'recu_numero', 'reference')
    autocomplete_fields = ('eleve', 'annee_scolaire', 'frais')