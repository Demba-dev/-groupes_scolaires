from django.urls import path

from . import views

app_name = 'scolarite'

urlpatterns = [
    # Années scolaires
    path('annees/', views.AnneeScolaireListView.as_view(), name='annees'),
    path('annees/nouvelle/', views.AnneeScolaireCreateView.as_view(), name='annee_create'),
    path('annees/<int:pk>/modifier/', views.AnneeScolaireUpdateView.as_view(), name='annee_update'),
    path('annees/<int:pk>/supprimer/', views.AnneeScolaireDeleteView.as_view(), name='annee_delete'),

    # Classes
    path('classes/', views.ClasseListView.as_view(), name='classes'),
    path('classes/nouvelle/', views.ClasseCreateView.as_view(), name='classe_create'),
    path('classes/<int:pk>/', views.ClasseDetailView.as_view(), name='classe_detail'),
    path('classes/<int:pk>/modifier/', views.ClasseUpdateView.as_view(), name='classe_update'),
    path('classes/<int:pk>/supprimer/', views.ClasseDeleteView.as_view(), name='classe_delete'),
    path('classes/<int:pk>/liste-imprimer/', views.liste_eleves_print, name='liste_eleves_print'),

    # Matières
    path('matieres/', views.MatiereListView.as_view(), name='matieres'),
    path('matieres/nouvelle/', views.MatiereCreateView.as_view(), name='matiere_create'),
    path('matieres/<int:pk>/modifier/', views.MatiereUpdateView.as_view(), name='matiere_update'),
    path('matieres/<int:pk>/supprimer/', views.MatiereDeleteView.as_view(), name='matiere_delete'),

    # Enseignements (affectations classe/matière/enseignant)
    path('enseignements/', views.EnseignementListView.as_view(), name='enseignements'),
    path('enseignements/nouveau/', views.EnseignementCreateView.as_view(), name='enseignement_create'),
    path('enseignements/<int:pk>/modifier/', views.EnseignementUpdateView.as_view(), name='enseignement_update'),
    path('enseignements/<int:pk>/supprimer/', views.EnseignementDeleteView.as_view(), name='enseignement_delete'),
]