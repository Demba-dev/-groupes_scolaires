from django.contrib import admin

from .models import AnneeScolaire, Classe, Enseignement, Matiere, Niveau


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'date_debut', 'date_fin', 'en_cours', 'cloturee')
    list_editable = ('en_cours', 'cloturee')
    search_fields = ('libelle',)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('ordre', 'libelle', 'cycle_libelle')
    ordering = ('ordre',)
    search_fields = ('libelle',)


class EnseignementInline(admin.TabularInline):
    model = Enseignement
    extra = 1
    autocomplete_fields = ('matiere', 'enseignant')


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'anne_scolaire', 'niveau', 'section', 'cycle_libelle', 'effectif', 'enseignant_titulaire', 'active')
    list_filter = ('anne_scolaire', 'niveau', 'active')
    search_fields = ('niveau__libelle', 'section')
    inlines = [EnseignementInline]
    autocomplete_fields = ('niveau', 'enseignant_titulaire')


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'coefficient')
    search_fields = ('nom', 'code')


@admin.register(Enseignement)
class EnseignementAdmin(admin.ModelAdmin):
    list_display = ('classe', 'matiere', 'enseignant', 'coefficient', 'horaire_hebdomadaire')
    list_filter = ('classe__anne_scolaire',)
    autocomplete_fields = ('classe', 'matiere', 'enseignant')
    search_fields = ('classe__niveau__libelle', 'classe__section', 'matiere__nom', 'enseignant__nom')