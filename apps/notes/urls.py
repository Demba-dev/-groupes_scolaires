from django.urls import path

from . import views

app_name = 'notes'

urlpatterns = [
    # Évaluations
    path('evaluations/', views.EvaluationListView.as_view(), name='evaluations'),
    path('evaluations/nouvelle/', views.EvaluationCreateView.as_view(), name='evaluation_create'),
    path('evaluations/<int:pk>/', views.EvaluationDetailView.as_view(), name='evaluation_detail'),
    path('evaluations/<int:pk>/modifier/', views.EvaluationUpdateView.as_view(), name='evaluation_update'),
    path('evaluations/<int:pk>/supprimer/', views.EvaluationDeleteView.as_view(), name='evaluation_delete'),
    path('evaluations/<int:pk>/notes/', views.saisie_notes, name='saisie_notes'),

    # Bulletins & classements
    path('bulletins/', views.BulletinListView.as_view(), name='bulletins'),
    path('bulletins/<int:pk>/', views.BulletinDetailView.as_view(), name='bulletin_detail'),
    path('bulletins/generer/<int:classe_id>/<str:periode>/', views.generer_bulletins, name='bulletins_generer'),
    path('classement/<int:classe_id>/<str:periode>/', views.classement_classe_view, name='classement'),
]