from django.urls import path

from . import views

app_name = 'eleves'

urlpatterns = [
    # Parents / tuteurs
    path('tuteurs/', views.TuteurListView.as_view(), name='tuteurs'),
    path('tuteurs/nouveau/', views.TuteurCreateView.as_view(), name='tuteur_create'),
    path('tuteurs/<int:pk>/modifier/', views.TuteurUpdateView.as_view(), name='tuteur_update'),
    path('tuteurs/<int:pk>/supprimer/', views.TuteurDeleteView.as_view(), name='tuteur_delete'),

    # Élèves
    path('', views.EleveListView.as_view(), name='liste'),
    path('nouveau/', views.EleveCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EleveDetailView.as_view(), name='eleve_detail'),
    path('<int:pk>/certificat/', views.certificat_scolarite, name='certificat'),
    path('<int:pk>/modifier/', views.EleveUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.EleveDeleteView.as_view(), name='delete'),

    # Inscriptions
    path('inscriptions/', views.InscriptionListView.as_view(), name='inscriptions'),
    path('inscriptions/nouvelle/', views.InscriptionCreateView.as_view(), name='inscription_create'),
    path('inscriptions/<int:pk>/modifier/', views.InscriptionUpdateView.as_view(), name='inscription_update'),
    path('inscriptions/<int:pk>/supprimer/', views.InscriptionDeleteView.as_view(), name='inscription_delete'),
    path('inscriptions/<int:pk>/cloturer/', views.cloturer_inscription, name='inscription_cloturer'),
]