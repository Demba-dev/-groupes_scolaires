"""Formulaires des élèves, parents/tuteurs et inscriptions."""

from django import forms

from apps.scolarite.models import AnneeScolaire, Classe

from .models import Eleve, Inscription, ParentTuteur


class DateInput(forms.DateInput):
    input_type = 'date'


class TuteurForm(forms.ModelForm):
    class Meta:
        model = ParentTuteur
        fields = ['nom', 'prenom', 'telephone', 'adresse', 'profession']


class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = [
            'matricule', 'nom', 'prenom', 'date_naissance', 'lieu_naissance',
            'sexe', 'adresse', 'photo', 'tuteur', 'lien_parent',
            'telephone_tuteur', 'statut',
        ]
        widgets = {
            'date_naissance': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tuteur'].required = False
        self.fields['photo'].required = False


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['eleve', 'annee_scolaire', 'classe', 'type_inscription', 'date_inscription']
        widgets = {
            'date_inscription': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['classe'].queryset = Classe.objects.select_related(
            'anne_scolaire', 'niveau'
        )
        if kwargs.get('initial'):
            annee = kwargs['initial'].get('annee_scolaire')
            if annee:
                self.fields['classe'].queryset = self.fields['classe'].queryset.filter(
                    anne_scolaire=annee
                )