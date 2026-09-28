"""Gestion des comptes utilisateurs."""

from django.contrib.auth import views as auth_views
from django.urls import path

from .views import (
    ConnexionView,
    UtilisateurCreateView,
    UtilisateurDeleteView,
    UtilisateurListView,
    UtilisateurUpdateView,
)

app_name = 'accounts'

urlpatterns = [
    path('connexion/', ConnexionView.as_view(), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),

    # Gestion des utilisateurs (Direction)
    path('utilisateurs/', UtilisateurListView.as_view(), name='utilisateurs'),
    path('utilisateurs/nouveau/', UtilisateurCreateView.as_view(), name='utilisateur_create'),
    path('utilisateurs/<int:pk>/modifier/', UtilisateurUpdateView.as_view(), name='utilisateur_update'),
    path('utilisateurs/<int:pk>/supprimer/', UtilisateurDeleteView.as_view(), name='utilisateur_delete'),
]