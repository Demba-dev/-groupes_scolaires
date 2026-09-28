"""Vues de la gestion financière."""

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from apps.core.permissions import DirectionRequiredMixin
from apps.eleves.models import Eleve
from apps.scolarite.models import AnneeScolaire, Classe

from .forms import FraisForm, PaiementForm
from .models import Frais, Paiement, montant_du, reste_a_payer, total_paye


class FraisListView(DirectionRequiredMixin, ListView):
    model = Frais
    paginate_by = 25
    template_name = 'finance/frais_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('annee_scolaire')
        annee = self.request.GET.get('annee', '')
        if annee:
            qs = qs.filter(annee_scolaire_id=annee)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        return ctx


class FraisCreateView(DirectionRequiredMixin, CreateView):
    model = Frais
    form_class = FraisForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('finance:frais')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouveau frais'
        ctx['cancel_url'] = reverse_lazy('finance:frais')
        return ctx


class FraisUpdateView(DirectionRequiredMixin, UpdateView):
    model = Frais
    form_class = FraisForm
    template_name = 'crud/form.html'
    success_url = reverse_lazy('finance:frais')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier {self.object.libelle}'
        ctx['cancel_url'] = reverse_lazy('finance:frais')
        return ctx


class FraisDeleteView(DirectionRequiredMixin, DeleteView):
    model = Frais
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('finance:frais')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Supprimer {self.object.libelle}'
        ctx['cancel_url'] = reverse_lazy('finance:frais')
        return ctx


class PaiementListView(DirectionRequiredMixin, ListView):
    model = Paiement
    paginate_by = 25
    template_name = 'finance/paiement_list.html'

    def get_queryset(self):
        qs = super().get_queryset().select_related('eleve', 'annee_scolaire', 'frais')
        annee = self.request.GET.get('annee', '')
        classe = self.request.GET.get('classe', '')
        q = self.request.GET.get('q', '').strip()
        if annee:
            qs = qs.filter(annee_scolaire_id=annee)
        if classe:
            ids = Eleve.objects.filter(
                inscriptions__classe_id=classe, inscriptions__statut='active'
            ).values_list('id', flat=True)
            qs = qs.filter(eleve_id__in=ids)
        if q:
            qs = qs.filter(
                Q(eleve__nom__icontains=q)
                | Q(eleve__prenom__icontains=q)
                | Q(eleve__matricule__icontains=q)
                | Q(recu_numero__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        ctx['classes'] = Classe.objects.select_related('anne_scolaire', 'niveau')
        return ctx


class PaiementCreateView(DirectionRequiredMixin, CreateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'finance/paiement_form.html'

    def get_initial(self):
        initial = super().get_initial()
        annee = AnneeScolaire.objects.filter(en_cours=True).first()
        if annee:
            initial['annee_scolaire'] = annee
        return initial

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouveau paiement'
        ctx['cancel_url'] = reverse_lazy('finance:paiements')
        return ctx

    def get_success_url(self):
        return f"{reverse_lazy('finance:detail_paiement', args=[self.object.pk])}"


class PaiementUpdateView(DirectionRequiredMixin, UpdateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'crud/form.html'

    def get_success_url(self):
        return f"{reverse_lazy('finance:detail_paiement', args=[self.object.pk])}"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier le paiement {self.object.recu_numero}'
        ctx['cancel_url'] = reverse_lazy('finance:detail_paiement', args=[self.object.pk])
        return ctx


class PaiementDeleteView(DirectionRequiredMixin, DeleteView):
    model = Paiement
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('finance:paiements')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Supprimer le paiement {self.object.recu_numero}'
        ctx['cancel_url'] = reverse_lazy('finance:paiements')
        return ctx


class PaiementDetailView(DirectionRequiredMixin, DetailView):
    """Reçu de paiement (page imprimable)."""

    model = Paiement
    template_name = 'finance/recu.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['total_annee'] = total_paye(self.object.eleve, self.object.annee_scolaire)
        return ctx


class ResteAPayerView(DirectionRequiredMixin, ListView):
    """Reste à payer par élève pour une classe et une année scolaire."""

    model = Eleve
    paginate_by = 50
    template_name = 'finance/reste_a_payer.html'

    def get_queryset(self):
        annee = self.request.GET.get('annee', '').strip()
        classe = self.request.GET.get('classe', '').strip()
        qs = Eleve.objects.filter(inscriptions__statut='active')
        if annee.isdigit():
            qs = qs.filter(inscriptions__annee_scolaire_id=int(annee))
        if classe.isdigit():
            qs = qs.filter(inscriptions__classe_id=int(classe))
        return qs.select_related('tuteur').distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        annee_id = self.request.GET.get('annee', '').strip()
        classe_id = self.request.GET.get('classe', '').strip()
        annee = None
        if annee_id.isdigit():
            annee = AnneeScolaire.objects.filter(pk=int(annee_id)).first()
        if not annee:
            annee = AnneeScolaire.objects.filter(en_cours=True).first()
        ctx['annee'] = annee
        ctx['annees'] = AnneeScolaire.objects.all()
        ctx['classe'] = Classe.objects.filter(pk=classe_id).first() if classe_id.isdigit() else None
        ctx['classes'] = Classe.objects.select_related('anne_scolaire', 'niveau')
        if annee:
            lignes = []
            for eleve in ctx['object_list']:
                lignes.append({
                    'eleve': eleve,
                    'montant_du': montant_du(eleve, annee),
                    'paye': total_paye(eleve, annee),
                    'reste': reste_a_payer(eleve, annee),
                })
            ctx['lignes'] = lignes
            ctx['total_du'] = sum(l['montant_du'] for l in lignes)
            ctx['total_paye'] = sum(l['paye'] for l in lignes)
            ctx['total_reste'] = sum(l['reste'] for l in lignes)
        return ctx