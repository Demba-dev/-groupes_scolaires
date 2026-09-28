from django.urls import path

from . import views

app_name = 'finance'

urlpatterns = [
    # Frais
    path('frais/', views.FraisListView.as_view(), name='frais'),
    path('frais/nouveau/', views.FraisCreateView.as_view(), name='frais_create'),
    path('frais/<int:pk>/modifier/', views.FraisUpdateView.as_view(), name='frais_update'),
    path('frais/<int:pk>/supprimer/', views.FraisDeleteView.as_view(), name='frais_delete'),

    # Paiements
    path('paiements/', views.PaiementListView.as_view(), name='paiements'),
    path('paiements/nouveau/', views.PaiementCreateView.as_view(), name='paiement_create'),
    path('paiements/<int:pk>/', views.PaiementDetailView.as_view(), name='detail_paiement'),
    path('paiements/<int:pk>/modifier/', views.PaiementUpdateView.as_view(), name='paiement_update'),
    path('paiements/<int:pk>/supprimer/', views.PaiementDeleteView.as_view(), name='paiement_delete'),

    # Reste à payer
    path('reste-a-payer/', views.ResteAPayerView.as_view(), name='reste_a_payer'),
]