from django.urls import path

from . import views

app_name = 'enseignants'

urlpatterns = [
    path('', views.EnseignantListView.as_view(), name='liste'),
    path('nouveau/', views.EnseignantCreateView.as_view(), name='create'),
    path('<int:pk>/', views.EnseignantDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.EnseignantUpdateView.as_view(), name='update'),
    path('<int:pk>/supprimer/', views.EnseignantDeleteView.as_view(), name='delete'),
]