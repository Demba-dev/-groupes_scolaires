from django.contrib import admin

from .models import Eleve, Inscription, ParentTuteur


class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 0
    autocomplete_fields = ('annee_scolaire', 'classe')
    readonly_fields = ('date_inscription',)


@admin.register(ParentTuteur)
class ParentTuteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'telephone', 'adresse', 'profession')
    search_fields = ('nom', 'prenom', 'telephone')


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'nom', 'prenom', 'sexe', 'date_naissance', 'tuteur', 'statut')
    list_filter = ('sexe', 'statut')
    search_fields = ('matricule', 'nom', 'prenom', 'tuteur__nom', 'tuteur__telephone')
    inlines = [InscriptionInline]
    autocomplete_fields = ('tuteur',)
    list_display_links = ('matricule', 'nom', 'prenom')


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'annee_scolaire', 'classe', 'type_inscription', 'statut', 'date_inscription')
    list_filter = ('annee_scolaire', 'type_inscription', 'statut')
    search_fields = ('eleve__nom', 'eleve__prenom', 'eleve__matricule')
    autocomplete_fields = ('eleve', 'annee_scolaire', 'classe')