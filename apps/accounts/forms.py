"""Formulaires des comptes utilisateurs."""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': "Nom d'utilisateur"}
        )
        self.fields['username'].label = "Nom d'utilisateur"
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Mot de passe'}
        )


class UtilisateurCreaForm(forms.ModelForm):
    password = forms.CharField(
        label='Mot de passe', widget=forms.PasswordInput()
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'telephone', 'role', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UtilisateurModifForm(forms.ModelForm):
    password = forms.CharField(
        label='Nouveau mot de passe',
        required=False,
        widget=forms.PasswordInput(),
        help_text='Laisse vide pour conserver le mot de passe actuel.',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'telephone', 'role', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user