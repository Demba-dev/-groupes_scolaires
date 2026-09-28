from django.urls import path

from . import views

app_name = 'presences'

urlpatterns = [
    path('appel/', views.feuille_presence, name='feuille'),
    path('', views.PresenceListView.as_view(), name='historique'),
    path('<int:pk>/modifier/', views.PresenceUpdateView.as_view(), name='modifier'),
]