"""Vues de gestion des élèves, parents/tuteurs et inscriptions."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from apps.core.permissions import DirectionRequiredMixin
from apps.scolarite.models import AnneeScolaire, Classe

from .forms import EleveForm, InscriptionForm, TuteurForm
from .models import Eleve, Inscription, ParentTuteur


class TuteurListView(DirectionRequiredMixin, ListView):
    model = ParentTuteur
    paginate_by = 25
    template_name = 'eleves/tuteur_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(nom__icontains=q)
                | Q(prenom__icontains=q)
                | Q(telephone__icontains=q)
            )
        return qs


class TuteurCreateView(DirectionRequiredMixin, CreateView):
    model = ParentTuteur
    form_class = TuteurForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:tuteurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouveau parent / tuteur'
        ctx['cancel_url'] = reverse_lazy('eleves:tuteurs')
        return ctx


class TuteurUpdateView(DirectionRequiredMixin, UpdateView):
    model = ParentTuteur
    form_class = TuteurForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:tuteurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier {self.object.nom_complet}'
        ctx['cancel_url'] = reverse_lazy('eleves:tuteurs')
        return ctx


class TuteurDeleteView(DirectionRequiredMixin, DeleteView):
    model = ParentTuteur
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('eleves:tuteurs')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object.nom_complet}"
        ctx['cancel_url'] = reverse_lazy('eleves:tuteurs')
        return ctx


class EleveListView(DirectionRequiredMixin, ListView):
    model = Eleve
    paginate_by = 25
    template_name = 'eleves/eleve_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('tuteur')
        q = self.request.GET.get('q', '').strip()
        classe = self.request.GET.get('classe', '')
        sexe = self.request.GET.get('sexe', '')
        statut = self.request.GET.get('statut', '')
        if q:
            qs = qs.filter(
                Q(matricule__icontains=q)
                | Q(nom__icontains=q)
                | Q(prenom__icontains=q)
                | Q(tuteur__nom__icontains=q)
                | Q(telephone_tuteur__icontains=q)
            )
        if classe:
            qs = qs.filter(inscriptions__classe_id=classe, inscriptions__statut='active')
        if sexe:
            qs = qs.filter(sexe=sexe)
        if statut:
            qs = qs.filter(statut=statut)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Classe.objects.select_related('anne_scolaire', 'niveau').order_by(
            '-anne_scolaire__date_debut', 'niveau__ordre', 'section'
        )
        return ctx


class EleveDetailView(DirectionRequiredMixin, DetailView):
    model = Eleve
    template_name = 'eleves/eleve_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        eleve = self.object
        ctx['inscriptions'] = eleve.inscriptions.select_related(
            'annee_scolaire', 'classe', 'classe__niveau'
        ).order_by('-annee_scolaire__date_debut')
        ctx['bulletins'] = eleve.bulletins.select_related(
            'classe', 'annee_scolaire'
        ).order_by('annee_scolaire__date_debut', 'periode')
        ctx['paiements'] = eleve.paiements.select_related(
            'annee_scolaire', 'frais'
        ).order_by('-date')
        from apps.finance.models import reste_a_payer

        ctx['reste_a_payer'] = (
            reste_a_payer(eleve, ctx['inscriptions'].first().annee_scolaire)
            if ctx['inscriptions'] else 0
        )
        return ctx


class EleveCreateView(DirectionRequiredMixin, CreateView):
    model = Eleve
    form_class = EleveForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvel élève'
        ctx['cancel_url'] = reverse_lazy('eleves:liste')
        return ctx


class EleveUpdateView(DirectionRequiredMixin, UpdateView):
    model = Eleve
    form_class = EleveForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Modifier {self.object.nom_complet}"
        ctx['cancel_url'] = self.object.get_absolute_url()
        return ctx


class EleveDeleteView(DirectionRequiredMixin, DeleteView):
    model = Eleve
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('eleves:liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer {self.object.nom_complet}"
        ctx['cancel_url'] = reverse_lazy('eleves:liste')
        return ctx


class InscriptionListView(DirectionRequiredMixin, ListView):
    model = Inscription
    paginate_by = 25
    template_name = 'eleves/inscription_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            'eleve', 'annee_scolaire', 'classe', 'classe__niveau'
        )
        annee = self.request.GET.get('annee', '')
        classe = self.request.GET.get('classe', '')
        q = self.request.GET.get('q', '').strip()
        if annee:
            qs = qs.filter(annee_scolaire_id=annee)
        if classe:
            qs = qs.filter(classe_id=classe)
        if q:
            qs = qs.filter(
                Q(eleve__matricule__icontains=q)
                | Q(eleve__nom__icontains=q)
                | Q(eleve__prenom__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        ctx['classes'] = Classe.objects.select_related('anne_scolaire', 'niveau')
        return ctx


class InscriptionCreateView(DirectionRequiredMixin, CreateView):
    model = Inscription
    form_class = InscriptionForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:inscriptions')

    def get_initial(self):
        initial = super().get_initial()
        annee = self.request.GET.get('annee')
        eleve = self.request.GET.get('eleve')
        if annee:
            initial['annee_scolaire'] = AnneeScolaire.objects.filter(pk=annee).first()
            initial['classe'] = None
        if eleve:
            initial['eleve'] = Eleve.objects.filter(pk=eleve).first()
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle inscription / réinscription'
        ctx['cancel_url'] = reverse_lazy('eleves:inscriptions')
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Inscription enregistrée.')
        return super().form_valid(form)


class InscriptionUpdateView(DirectionRequiredMixin, UpdateView):
    model = Inscription
    form_class = InscriptionForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('eleves:inscriptions')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier l\'inscription de {self.object.eleve.nom_complet}'
        ctx['cancel_url'] = reverse_lazy('eleves:inscriptions')
        return ctx


class InscriptionDeleteView(DirectionRequiredMixin, DeleteView):
    model = Inscription
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('eleves:inscriptions')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"Supprimer l'inscription de {self.object.eleve.nom_complet}"
        ctx['cancel_url'] = reverse_lazy('eleves:inscriptions')
        return ctx


def cloturer_inscription(request, pk):
    """Clôture l'inscription (ex. transfert en cours d'année)."""
    inscription = get_object_or_404(Inscription, pk=pk)
    inscription.statut = 'cloturee'
    inscription.save(update_fields=['statut'])
    return redirect('eleves:eleve_detail', pk=inscription.eleve.pk)


@login_required
def certificat_scolarite(request, pk):
    """Certificat de scolarité d'un élève pour une année scolaire (imprimable)."""
    eleve = get_object_or_404(Eleve, pk=pk)
    annee_id = request.GET.get('annee') or \
        AnneeScolaire.objects.filter(en_cours=True).values_list('id', flat=True).first()
    annee = get_object_or_404(AnneeScolaire, pk=annee_id) if annee_id else None
    inscription = None
    if annee:
        inscription = (
            eleve.inscriptions.select_related('classe', 'classe__anne_scolaire', 'classe__niveau')
            .filter(annee_scolaire=annee)
            .first()
        )
    return render(request, 'documents/certificat_scolarite.html', {
        'eleve': eleve,
        'annee': annee,
        'inscription': inscription,
    })