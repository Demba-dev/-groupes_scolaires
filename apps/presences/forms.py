"""Formulaires des présences."""

from django import forms

from .models import Presence


class DateInput(forms.DateInput):
    input_type = 'date'


class PresenceUpdateForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ['statut', 'justifie', 'motif']
        widgets = {'motif': forms.TextInput(attrs={'placeholder': 'Ex. : certificat médical'})}