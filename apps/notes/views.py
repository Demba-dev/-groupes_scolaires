"""Vues des évaluations, saisie des notes, bulletins et classements."""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from apps.accounts.models import ROLE_DIRECTION, ROLE_ENSEIGNANT
from apps.core.permissions import DirectionRequiredMixin, EnseignantAccessMixin, role_required
from apps.scolarite.models import AnneeScolaire, Classe

from . import services
from .forms import EvaluationForm, classes_autorisees
from .models import Bulletin, Evaluation, Note, PERIODE_CHOICES


def evaluations_authorees(user):
    """Queryset d'évaluations restreint selon le rôle."""
    qs = Evaluation.objects.select_related(
        'classe', 'classe__niveau', 'matiere', 'annee_scolaire'
    )
    if user.role == ROLE_DIRECTION:
        return qs
    enseignant = getattr(user, 'enseignant', None)
    if not enseignant:
        return qs.none()
    classes_ids = enseignant.classes.values_list('id', flat=True)
    return qs.filter(classe_id__in=classes_ids)


class EvaluationListView(EnseignantAccessMixin, ListView):
    model = Evaluation
    paginate_by = 25
    template_name = 'notes/evaluation_list.html'

    def get_queryset(self):
        qs = evaluations_authorees(self.request.user)
        annee = self.request.GET.get('annee', '')
        classe = self.request.GET.get('classe', '')
        periode = self.request.GET.get('periode', '')
        matiere = self.request.GET.get('matiere', '')
        if annee:
            qs = qs.filter(annee_scolaire_id=annee)
        if classe:
            qs = qs.filter(classe_id=classe)
        if periode:
            qs = qs.filter(periode=periode)
        if matiere:
            qs = qs.filter(matiere_id=matiere)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        ctx['classes'] = classes_autorisees(self.request.user)
        ctx['periodes'] = PERIODE_CHOICES
        ctx['matieres'] = self.request.user.role == ROLE_DIRECTION
        return ctx


class EvaluationCreateView(EnseignantAccessMixin, CreateView):
    model = Evaluation
    template_name = 'crud/form.html'
    success_url = reverse_lazy('notes:evaluations')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_form_class(self):
        return EvaluationForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'Nouvelle évaluation'
        ctx['cancel_url'] = reverse_lazy('notes:evaluations')
        return ctx


class EvaluationUpdateView(EnseignantAccessMixin, UpdateView):
    model = Evaluation
    template_name = 'crud/form.html'
    success_url = reverse_lazy('notes:evaluations')

    def get_queryset(self):
        return evaluations_authorees(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_form_class(self):
        return EvaluationForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Modifier {self.object.titre}'
        ctx['cancel_url'] = reverse_lazy('notes:evaluations')
        return ctx


class EvaluationDeleteView(EnseignantAccessMixin, DeleteView):
    model = Evaluation
    template_name = 'crud/confirm_delete.html'
    success_url = reverse_lazy('notes:evaluations')

    def get_queryset(self):
        return evaluations_authorees(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f'Supprimer {self.object.titre}'
        ctx['cancel_url'] = reverse_lazy('notes:evaluations')
        return ctx


class EvaluationDetailView(EnseignantAccessMixin, DetailView):
    model = Evaluation
    template_name = 'notes/evaluation_detail.html'

    def get_queryset(self):
        return evaluations_authorees(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        evaluation = self.object
        students = list(
            evaluation.classe.inscriptions.filter(
                statut='active', annee_scolaire=evaluation.annee_scolaire
            ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')
        )
        notes = {n.eleve_id: n for n in evaluation.notes.select_related('eleve')}
        ctx['lignes'] = [
            {'inscription': ins, 'note': notes.get(ins.eleve_id)}
            for ins in students
        ]
        return ctx


@login_required
def saisie_notes(request, pk):
    """Saisie / modification des notes des élèves d'une classe pour une évaluation."""
    evaluation = get_object_or_404(Evaluation, pk=pk)
    _exiger_classe_autorisee(request.user, evaluation.classe)
    if not (
        request.user.role == ROLE_DIRECTION
        or request.user.role == ROLE_ENSEIGNANT
    ):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    eleves = [
        ins.eleve
        for ins in evaluation.classe.inscriptions.filter(
            statut='active', annee_scolaire=evaluation.annee_scolaire
        ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')
    ]

    if request.method == 'POST':
        bareme = evaluation.bareme
        probabilite_erreur = 0
        for eleve in eleves:
            cle = f'note_{eleve.id}'
            brut = request.POST.get(cle, '').strip().replace(',', '.')
            valeur = None
            if brut:
                try:
                    valeur = Decimal(brut)
                except Exception:
                    messages.warning(request, f"Note non reconnue pour {eleve.nom_complet}.")
                    continue
                if valeur < 0 or valeur > bareme:
                    messages.warning(
                        request,
                        f"Note hors barème (/ {bareme}) pour {eleve.nom_complet}.",
                    )
                    continue
            if valeur is None:
                Note.objects.filter(evaluation=evaluation, eleve=eleve).delete()
            else:
                Note.objects.update_or_create(
                    evaluation=evaluation,
                    eleve=eleve,
                    defaults={'valeur': valeur},
                )
                probabilite_erreur += 1
        messages.success(
            request,
            f'{probabilite_erreur} note(s) enregistrée(s) pour « {evaluation.titre} ».',
        )
        return redirect('notes:evaluation_detail', pk=evaluation.pk)

    existantes = {n.eleve_id: n for n in evaluation.notes.all()}
    lignes = [{'eleve': e, 'note': existantes.get(e.id)} for e in eleves]
    return render(request, 'notes/saisie_notes.html', {
        'evaluation': evaluation,
        'lignes': lignes,
    })


class BulletinListView(EnseignantAccessMixin, ListView):
    model = Bulletin
    paginate_by = 25
    template_name = 'notes/bulletin_list.html'

    def get_queryset(self):
        qs = Bulletin.objects.select_related('eleve', 'classe', 'annee_scolaire')
        annee = self.request.GET.get('annee', '')
        classe = self.request.GET.get('classe', '')
        periode = self.request.GET.get('periode', '')
        if annee:
            qs = qs.filter(annee_scolaire_id=annee)
        if classe:
            qs = qs.filter(classe_id=classe)
        if periode:
            qs = qs.filter(periode=periode)
        if self.request.user.role != ROLE_DIRECTION:
            enseignant = getattr(self.request.user, 'enseignant', None)
            if not enseignant:
                return qs.none()
            qs = qs.filter(classe_id__in=enseignant.classes.values_list('id', flat=True))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['annees'] = AnneeScolaire.objects.all()
        ctx['classes'] = classes_autorisees(self.request.user)
        ctx['periodes'] = PERIODE_CHOICES
        return ctx


@login_required
def generer_bulletins(request, classe_id, periode):
    """Régénère les bulletins de toute une classe pour une période."""
    classe = get_object_or_404(Classe, pk=classe_id)
    _exiger_classe_autorisee(request.user, classe)
    n = services.generer_bulletins_classe(
        classe, classe.anne_scolaire, periode
    )
    messages.success(request, f'{n} bulletin(s) généré(s) pour {classe.nom} ({periode}).')
    return redirect(f"{reverse('notes:bulletins')}?classe={classe_id}&periode={periode}")


def _exiger_classe_autorisee(user, classe):
    """Lève PermissionDenied si l'utilisateur (non direction) n'a pas cette classe."""
    if user.role == ROLE_DIRECTION:
        return
    enseignant = getattr(user, 'enseignant', None)
    autorise = bool(enseignant and classe.id in set(enseignant.classes.values_list('id', flat=True)))
    if not autorise:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied


class BulletinDetailView(EnseignantAccessMixin, DetailView):
    model = Bulletin
    template_name = 'notes/bulletin_detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        bulletin = self.object
        lignes = services.lignes_matiere(
            bulletin.eleve, bulletin.classe, bulletin.annee_scolaire, bulletin.periode
        )
        ctx['lignes'] = lignes
        ctx['moyenne'] = services.moyenne_ponderee(lignes)
        from django.conf import settings

        ctx['note_base'] = settings.NOTE_BASE
        return ctx


@login_required
def classement_classe_view(request, classe_id, periode):
    classe = get_object_or_404(Classe, pk=classe_id)
    _exiger_classe_autorisee(request.user, classe)
    resultats = services.classement_classe(
        classe, classe.anne_scolaire, periode
    )
    lignes_ranges = list(services.attribuer_rangs(resultats))
    return render(request, 'notes/classement.html', {
        'classe': classe,
        'periode': periode,
        'annee': classe.anne_scolaire,
        'lignes_ranges': lignes_ranges,
    })