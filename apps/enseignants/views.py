"""Vues de gestion des enseignants."""

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from apps.core.permissions import DirectionRequiredMixin

from .forms import EnseignantForm
from .models import Enseignant


class EnseignantListView(DirectionRequiredMixin, ListView):
    model = Enseignant
    paginate_by = 25
    template_name = 'enseignants/enseignant_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('user')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(matricule__icontains=q)
                | Q(nom__icontains=q)
                | Q(prenom__icontains=q)
                | Q(telephone__icontains=q)
            )
        return qs


class EnseignantDetailView(DirectionRequiredMixin, DetailView):
    model = Enseignant
    template_name = 'enseignants/enseignant_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes_dirigees'] = self.object.classes_dirigees.select_related(
            'anne_scolaire', 'niveau'
        )
        ctx['enseignements'] = self.object.enseignements.select_related(
            'classe', 'classe__niveau', 'matiere'
        )
        return ctx


class EnseignantCreateView(DirectionRequiredMixin, CreateView):
    model = Enseignant
    form_class = EnseignantForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('enseignants:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvel enseignant'
        ctx['cancel_url'] = reverse_lazy('enseignants:liste')
        return ctx


class EnseignantUpdateView(DirectionRequiredMixin, UpdateView):
    model = Enseignant
    form_class = EnseignantForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('enseignants:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Modifier {self.object.nom_complet}"
        ctx['cancel_url'] = reverse_lazy('enseignants:liste')
        return ctx


class EnseignantDeleteView(DirectionRequiredMixin, DeleteView):
    model = Enseignant
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('enseignants:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Supprimer {self.object.nom_complet}'
        ctx['cancel_url'] = reverse_lazy('enseignants:liste')
        return ctx