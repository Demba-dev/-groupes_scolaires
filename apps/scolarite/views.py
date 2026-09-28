"""Vues de gestion de l'organisation pédagogique (réservées à la direction)."""

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.core.permissions import DirectionRequiredMixin

from .forms import AnneeScolaireForm, ClasseForm, EnseignementForm, MatiereForm
from .models import AnneeScolaire, Classe, Enseignement, Matiere


class AnneeScolaireListView(DirectionRequiredMixin, ListView):
    model = AnneeScolaire
    paginate_by = 25
    template_name = 'scolarite/annee_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(libelle__icontains=q)
        return qs


class AnneeScolaireCreateView(DirectionRequiredMixin, CreateView):
    model = AnneeScolaire
    form_class = AnneeScolaireForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:annees')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle année scolaire'
        ctx['cancel_url'] = reverse_lazy('scolarite:annees')
        return ctx


class AnneeScolaireUpdateView(DirectionRequiredMixin, UpdateView):
    model = AnneeScolaire
    form_class = AnneeScolaireForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:annees')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Modifier {self.object}"
        ctx['cancel_url'] = reverse_lazy('scolarite:annees')
        return ctx


class AnneeScolaireDeleteView(DirectionRequiredMixin, DeleteView):
    model = AnneeScolaire
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('scolarite:annees')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object}"
        ctx['cancel_url'] = reverse_lazy('scolarite:annees')
        return ctx


class ClasseListView(DirectionRequiredMixin, ListView):
    model = Classe
    paginate_by = 25
    template_name = 'scolarite/classe_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('anne_scolaire', 'niveau', 'enseignant_titulaire')
        annee = self.request.GET.get('annee', '')
        cycle = self.request.GET.get('cycle', '')
        q = self.request.GET.get('q', '').strip()
        if annee:
            qs = qs.filter(anne_scolaire_id=annee)
        if cycle == 'premier':
            qs = qs.filter(niveau__ordre__lte=6)
        elif cycle == 'deuxieme':
            qs = qs.filter(niveau__ordre__gt=6)
        if q:
            qs = qs.filter(niveau__libelle__icontains=q) | qs.filter(section__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        return ctx


class ClasseCreateView(DirectionRequiredMixin, CreateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:classes')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle classe'
        ctx['cancel_url'] = reverse_lazy('scolarite:classes')
        return ctx


class ClasseUpdateView(DirectionRequiredMixin, UpdateView):
    model = Classe
    form_class = ClasseForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:classes')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier la classe {self.object.nom}'
        ctx['cancel_url'] = reverse_lazy('scolarite:classes')
        return ctx


class ClasseDeleteView(DirectionRequiredMixin, DeleteView):
    model = Classe
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('scolarite:classes')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer la classe {self.object.nom}"
        ctx['cancel_url'] = reverse_lazy('scolarite:classes')
        return ctx


class ClasseDetailView(DetailView):
    model = Classe
    template_name = 'scolarite/classe_detail.html'

    def get_queryset(self):
        qs = Classe.objects.select_related(
            'anne_scolaire', 'niveau', 'enseignant_titulaire'
        )
        if getattr(self.request.user, 'role', None) == 'direction':
            return qs
        enseignant = getattr(self.request.user, 'enseignant', None)
        if not enseignant:
            return qs.none()
        return qs.filter(id__in=enseignant.classes.values_list('id', flat=True))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['inscriptions'] = self.object.inscriptions.filter(
            statut='active'
        ).select_related('eleve', 'eleve__tuteur').order_by('eleve__nom', 'eleve__prenom')
        ctx['enseignements'] = self.object.enseignements.select_related(
            'matiere', 'enseignant'
        ).order_by('matiere__nom')
        return ctx


@login_required
def liste_eleves_print(request, pk):
    """Liste d'élèves d'une classe (page imprimable)."""
    classe = get_object_or_404(
        Classe.objects.select_related('anne_scolaire', 'niveau'), pk=pk
    )
    inscriptions = classe.inscriptions.filter(statut='active').select_related(
        'eleve', 'eleve__tuteur'
    ).order_by('eleve__nom', 'eleve__prenom')
    return render(request, 'documents/liste_eleves.html', {
        'classe': classe,
        'inscriptions': inscriptions,
    })


class MatiereListView(DirectionRequiredMixin, ListView):
    model = Matiere
    paginate_by = 25
    template_name = 'scolarite/matiere_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(nom__icontains=q) | qs.filter(code__icontains=q)
        return qs


class MatiereCreateView(DirectionRequiredMixin, CreateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:matieres')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle matière'
        ctx['cancel_url'] = reverse_lazy('scolarite:matieres')
        return ctx


class MatiereUpdateView(DirectionRequiredMixin, UpdateView):
    model = Matiere
    form_class = MatiereForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:matieres')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Modifier {self.object.nom}"
        ctx['cancel_url'] = reverse_lazy('scolarite:matieres')
        return ctx


class MatiereDeleteView(DirectionRequiredMixin, DeleteView):
    model = Matiere
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('scolarite:matieres')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object.nom}"
        ctx['cancel_url'] = reverse_lazy('scolarite:matieres')
        return ctx


class EnseignementListView(DirectionRequiredMixin, ListView):
    model = Enseignement
    paginate_by = 25
    template_name = 'scolarite/enseignement_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('classe', 'classe__niveau', 'matiere', 'enseignant')
        annee = self.request.GET.get('annee', '')
        q = self.request.GET.get('q', '').strip()
        if annee:
            qs = qs.filter(classe__anne_scolaire_id=annee)
        if q:
            qs = qs.filter(
                matiere__nom__icontains=q
            ) | qs.filter(enseignant__nom__icontains=q) | qs.filter(enseignant__prenom__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        return ctx


class EnseignementCreateView(DirectionRequiredMixin, CreateView):
    model = Enseignement
    form_class = EnseignementForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:enseignements')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle affectation (classe / matière / enseignant)'
        ctx['cancel_url'] = reverse_lazy('scolarite:enseignements')
        return ctx


class EnseignementUpdateView(DirectionRequiredMixin, UpdateView):
    model = Enseignement
    form_class = EnseignementForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('scolarite:enseignements')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Modifier {self.object}"
        ctx['cancel_url'] = reverse_lazy('scolarite:enseignements')
        return ctx


class EnseignementDeleteView(DirectionRequiredMixin, DeleteView):
    model = Enseignement
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('scolarite:enseignements')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object}"
        ctx['cancel_url'] = reverse_lazy('scolarite:enseignements')
        return ctx