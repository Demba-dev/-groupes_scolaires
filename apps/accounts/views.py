"""Vues d'authentification et de gestion des utilisateurs."""

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DeleteView, ListView
from django.views.generic.edit import CreateView, UpdateView

from apps.core.permissions import DirectionRequiredMixin

from .forms import LoginForm, UtilisateurCreaForm, UtilisateurModifForm
from .models import User

class ConnexionView(auth_views.LoginView):
    template_name = 'registration/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True


class UtilisateurListView(DirectionRequiredMixin, ListView):
    model = User
    paginate_by = 25
    template_name = 'accounts/utilisateur_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.GET.get('role', '')
        q = self.request.GET.get('q', '').strip()
        if role:
            qs = qs.filter(role=role)
        if q:
            qs = qs.filter(
                Q(username__icontains=q)
                | Q(first_name__icontains=q)
                | Q(last_name__icontains=q)
                | Q(telephone__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ROLE_CHOICES'] = User._meta.get_field('role').choices
        return ctx


class UtilisateurCreateView(DirectionRequiredMixin, CreateView):
    model = User
    form_class = UtilisateurCreaForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:utilisateurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvel utilisateur'
        ctx['cancel_url'] = reverse_lazy('accounts:utilisateurs')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Utilisateur créé.')
        return super().form_valid(form)


class UtilisateurUpdateView(DirectionRequiredMixin, UpdateView):
    model = User
    form_class = UtilisateurModifForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('accounts:utilisateurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier {self.object.username}'
        ctx['cancel_url'] = reverse_lazy('accounts:utilisateurs')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Utilisateur mis à jour.')
        return super().form_valid(form)


class UtilisateurDeleteView(DirectionRequiredMixin, DeleteView):
    model = User
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('accounts:utilisateurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object.username}"
        ctx['cancel_url'] = reverse_lazy('accounts:utilisateurs')
        return ctx