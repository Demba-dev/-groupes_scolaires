"""Formulaires des enseignants (avec création optionnelle d'un compte)."""

from django import forms
from django.contrib.auth import get_user_model

from apps.accounts.models import ROLE_ENSEIGNANT

from .models import Enseignant

User = get_user_model()


class DateInput(forms.DateInput):
    input_type = 'date'


class EnseignantForm(forms.ModelForm):
    creer_compte = forms.BooleanField(
        label='Créer un compte de connexion',
        required=False,
        help_text='Crée un utilisateur (rôle « Enseignant ») lié à cette fiche.',
    )
    username = forms.CharField(label='Nom d\'utilisateur', required=False)
    password = forms.CharField(
        label='Mot de passe',
        required=False,
        widget=forms.PasswordInput(),
    )

    class Meta:
        model = Enseignant
        fields = [
            'matricule', 'user', 'nom', 'prenom', 'sexe', 'date_naissance',
            'telephone', 'adresse', 'specialite', 'actif',
        ]
        widgets = {
            'date_naissance': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].help_text = (
            'Si la fiche existe déjà : choisis un compte existant. '
            'Sinon, coche « Créer un compte ».'
        )
        self.fields['user'].required = False

    def clean(self):
        donnees = super().clean()
        creer = donnees.get('creer_compte')
        username = donnees.get('username')
        password = donnees.get('password')
        user = donnees.get('user')

        if creer:
            if not username:
                self.add_error('username', "Choisis un nom d'utilisateur.")
            if not password:
                self.add_error('password', 'Le mot de passe est obligatoire.')
            if username and User.objects.filter(username=username).exists():
                self.add_error('username', "Ce nom d'utilisateur existe déjà.")
            if user:
                self.add_error('user', 'Un compte est déjà sélectionné : inutile d\'en créer un.')
        return donnees

    def save(self, commit=True):
        enseignant = super().save(commit=False)
        if self.cleaned_data.get('creer_compte'):
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                password=self.cleaned_data['password'],
                role=ROLE_ENSEIGNANT,
                first_name=enseignant.prenom,
                last_name=enseignant.nom,
            )
            enseignant.user = user
        if commit:
            enseignant.save()
        return enseignant