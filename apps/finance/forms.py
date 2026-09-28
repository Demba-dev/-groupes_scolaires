"""Formulaires de la gestion financière."""

from django import forms

from .models import Frais, Paiement


class DateInput(forms.DateInput):
    input_type = 'date'


class FraisForm(forms.ModelForm):
    class Meta:
        model = Frais
        fields = ['libelle', 'montant', 'annee_scolaire', 'obligatoire']


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = [
            'eleve', 'annee_scolaire', 'frais', 'montant',
            'mode', 'date', 'reference', 'commentaire',
        ]
        widgets = {
            'date': DateInput(),
        }