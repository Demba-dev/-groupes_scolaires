from django.contrib import admin

from .models import Bulletin, Evaluation, Note


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    autocomplete_fields = ('eleve',)


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'classe', 'matiere', 'type_evaluation', 'periode', 'date', 'bareme')
    list_filter = ('classe__anne_scolaire', 'type_evaluation', 'periode', 'matiere')
    search_fields = ('titre', 'classe__niveau__libelle', 'matiere__nom')
    autocomplete_fields = ('classe', 'matiere', 'annee_scolaire')
    inlines = [NoteInline]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'evaluation', 'valeur')
    search_fields = ('eleve__nom', 'eleve__prenom')
    autocomplete_fields = ('eleve', 'evaluation')


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'classe', 'annee_scolaire', 'periode', 'moyenne_generale', 'rang', 'decision')
    list_filter = ('annee_scolaire', 'classe', 'periode')
    search_fields = ('eleve__nom', 'eleve__prenom')
    autocomplete_fields = ('eleve', 'classe', 'annee_scolaire')