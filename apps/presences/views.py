"""Vues des présences (appel et historique)."""

import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, UpdateView

from apps.accounts.models import ROLE_DIRECTION
from apps.core.permissions import EnseignantAccessMixin
from apps.scolarite.models import Classe

from .forms import PresenceUpdateForm
from .models import Presence, STATUT_PRESENCE_CHOICES


def presences_autorisees(user):
    qs = Presence.objects.select_related('eleve', 'classe', 'classe__niveau')
    if user.role == ROLE_DIRECTION:
        return qs
    enseignant = getattr(user, 'enseignant', None)
    if not enseignant:
        return qs.none()
    return qs.filter(classe_id__in=enseignant.classes.values_list('id', flat=True))


def _parse_date(valeur):
    try:
        return datetime.date.fromisoformat(valeur)
    except (ValueError, TypeError):
        return None


@login_required
def feuille_presence(request):
    """Appel de présence d'une classe pour une date.

    GET  : choix de la classe et de la date (par défaut : aujourd'hui).
    POST : enregistre les statuts envoyés (présent / absent / retard).
    """
    if request.user.role not in (ROLE_DIRECTION, 'enseignant'):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    classes = Classe.objects.select_related('anne_scolaire', 'niveau').filter(
        anne_scolaire__en_cours=True,
        active=True,
    ).order_by('niveau__ordre', 'section')
    if request.user.role != ROLE_DIRECTION:
        enseignant = getattr(request.user, 'enseignant', None)
        if not enseignant:
            classes = classes.none()
        else:
            classes = classes.filter(id__in=enseignant.classes.values_list('id', flat=True))

    classe_id = request.GET.get('classe') or request.POST.get('classe')
    date_str = request.GET.get('date') or request.POST.get('date') or timezone.localdate().isoformat()
    aujourd_hui = _parse_date(date_str) or timezone.localdate()

    classe = None
    lignes = []
    if classe_id:
        classe = get_object_or_404(Classe, pk=classe_id)
        inscriptions = classe.inscriptions.filter(
            statut='active', annee_scolaire__en_cours=True
        ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')

        if request.method == 'POST':
            for ins in inscriptions:
                eleve = ins.eleve
                statut_poste = request.POST.get(f'statut_{eleve.id}', '').strip()
                justifie = request.POST.get(f'justifie_{eleve.id}') == 'on'
                motif = request.POST.get(f'motif_{eleve.id}', '').strip()
                if statut_poste not in dict(STATUT_PRESENCE_CHOICES):
                    Presence.objects.filter(eleve=eleve, date=aujourd_hui).delete()
                    continue
                Presence.objects.update_or_create(
                    eleve=eleve,
                    date=aujourd_hui,
                    defaults={
                        'classe': classe,
                        'statut': statut_poste,
                        'justifie': justifie,
                        'motif': motif,
                        'enregistre_par': request.user,
                    },
                )
            messages.success(
                request,
                f"Appel enregistré pour {classe.nom} le {aujourd_hui}.",
            )
            return redirect(f"{reverse_lazy('presences:feuille')}?classe={classe_id}&date={date_str}")

        presentes = {
            p.eleve_id: p
            for p in Presence.objects.filter(
                classe=classe, date=aujourd_hui
            ).select_related('eleve')
        }
        lignes = [
            {'inscription': ins, 'presence': presentes.get(ins.eleve_id)}
            for ins in inscriptions
        ]

    return render(request, 'presences/feuille_presence.html', {
        'classes': classes,
        'classe': classe,
        'lignes': lignes,
        'date': aujourd_hui,
        'statuts': STATUT_PRESENCE_CHOICES,
    })


class PresenceListView(EnseignantAccessMixin, ListView):
    model = Presence
    paginate_by = 25
    template_name = 'presences/presence_list.html'

    def get_queryset(self):
        qs = presences_autorisees(self.request.user)
        classe = self.request.GET.get('classe', '')
        jour = self.request.GET.get('date', '')
        statut = self.request.GET.get('statut', '')
        justifie = self.request.GET.get('justifie', '')
        q = self.request.GET.get('q', '').strip()
        if classe:
            qs = qs.filter(classe_id=classe)
        if jour:
            parsed = _parse_date(jour)
            if parsed:
                qs = qs.filter(date=parsed)
        if statut:
            qs = qs.filter(statut=statut)
        if justifie in ('oui', 'non'):
            qs = qs.filter(justifie=(justifie == 'oui'))
        if q:
            qs = qs.filter(
                Q(eleve__nom__icontains=q)
                | Q(eleve__prenom__icontains=q)
                | Q(motif__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['classes'] = Classe.objects.select_related('anne_scolaire', 'niveau')
        ctx['statuts'] = STATUT_PRESENCE_CHOICES
        return ctx


class PresenceUpdateView(EnseignantAccessMixin, UpdateView):
    """Modifie une présence (justification…)."""

    model = Presence
    form_class = PresenceUpdateForm
    template_name = 'crud/form.html'

    def get_queryset(self):
        return presences_autorisees(self.request.user)

    def get_success_url(self):
        return f"{reverse_lazy('presences:historique')}?classe={self.object.classe_id}"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = f"{self.object.eleve.nom_complet} — {self.object.date}"
        ctx['cancel_url'] = reverse_lazy('presences:historique')
        return ctx