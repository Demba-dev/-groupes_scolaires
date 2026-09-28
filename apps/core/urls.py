from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.tableau_de_bord, name='dashboard'),
]