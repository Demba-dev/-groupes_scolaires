"""Formulaires de l'organisation pédagogique."""

from django import forms

from .models import AnneeScolaire, Classe, Enseignement, Matiere


class DateInput(forms.DateInput):
    input_type = 'date'


class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['libelle', 'date_debut', 'date_fin', 'en_cours', 'cloturee']
        widgets = {
            'date_debut': DateInput(),
            'date_fin': DateInput(),
        }

    def clean(self):
        donnees = super().clean()
        debut = donnees.get('date_debut')
        fin = donnees.get('date_fin')
        if debut and fin and fin < debut:
            self.add_error('date_fin', 'La date de fin doit être après la date de début.')
        if donnees.get('en_cours'):
            AnneeScolaire.objects.filter(en_cours=True).exclude(pk=self.instance.pk).update(en_cours=False)
        return donnees

    def clean_libelle(self):
        libelle = self.cleaned_data['libelle'].strip()
        if not libelle:
            raise forms.ValidationError("Ce champ est obligatoire.")
        return libelle


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = [
            'anne_scolaire', 'niveau', 'section',
            'enseignant_titulaire', 'capacite_max', 'active',
        ]
        widgets = {
            'capacite_max': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        annees = self.fields['anne_scolaire'].queryset
        self.fields['anne_scolaire'].queryset = annees.order_by('-date_debut')


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom', 'code', 'coefficient', 'description']


class EnseignementForm(forms.ModelForm):
    class Meta:
        model = Enseignement
        fields = ['classe', 'matiere', 'enseignant', 'coefficient', 'horaire_hebdomadaire']
        widgets = {
            'coefficient': forms.NumberInput(attrs={'min': 1}),
            'horaire_hebdomadaire': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].queryset = Classe.objects.select_related(
            'anne_scolaire', 'niveau'
        ).order_by('-anne_scolaire__date_debut', 'niveau__ordre', 'section')