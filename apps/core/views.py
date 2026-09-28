"""Vue du tableau de bord principal."""

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.shortcuts import render
from django.utils import timezone

from apps.eleves.models import Eleve
from apps.enseignants.models import Enseignant
from apps.finance.models import Paiement
from apps.notes.models import Bulletin
from apps.presences.models import Presence
from apps.scolarite.models import AnneeScolaire, Classe


@login_required
def tableau_de_bord(request):
    annee = AnneeScolaire.objects.filter(en_cours=True).first()
    today = timezone.localdate()
    contexte = {
        'annee': annee,
        'aujourd_hui': today,
    }

    # --- Elèves / classes ---
    eleves_actifs = Eleve.objects.filter(statut='actif')
    contexte['total_eleves'] = eleves_actifs.count()
    contexte['total_enseignants'] = Enseignant.objects.filter(actif=True).count()

    if annee:
        classes = Classe.objects.filter(anne_scolaire=annee, active=True)
        contexte['classes'] = classes

        contexte['effectif_cycle_1'] = sum(
            c.effectif for c in classes if c.cycle == 'premier'
        )
        contexte['effectif_cycle_2'] = sum(
            c.effectif for c in classes if c.cycle == 'deuxieme'
        )

        # Répartition des effectifs par classe (avec inscriptions actives)
        reps = (
            classes.annotate(effectif_annee=Count('inscriptions', filter=Q(inscriptions__statut='active')))
            .order_by('niveau__ordre', 'section')
        )
        rep_cycle = [0, 0]
        par_classe = []
        for c in reps:
            par_classe.append({'classe': c.nom, 'effectif': c.effectif_annee, 'cycle': c.cycle})
            if c.cycle == 'premier':
                rep_cycle[0] += c.effectif_annee
            else:
                rep_cycle[1] += c.effectif_annee
        contexte['effectifs_par_classe'] = par_classe
        contexte['repartition_cycles'] = rep_cycle

    # --- Présences du jour (si année active) ---
    presences_du_jour = Presence.objects.filter(date=today)
    presentes = presences_du_jour.filter(statut='present').count()
    absentes = presences_du_jour.filter(statut='absent').count()
    retards = presences_du_jour.filter(statut='retard').count()
    contexte['presences'] = {
        'total': presences_du_jour.count(),
        'presentes': presentes,
        'absentes': absentes,
        'retards': retards,
    }

    # --- Résultats / bulletins ---
    bulletins = Bulletin.objects.all()
    contexte['total_bulletins'] = bulletins.count()
    contexte['bulletins_recents'] = bulletins.select_related(
        'eleve', 'classe', 'annee_scolaire'
    ).order_by('-cree_le')[:5]

    # --- Finance (année en cours) ---
    if annee:
        encaisse = (
            Paiement.objects.filter(annee_scolaire=annee)
            .aggregate(total=Sum('montant'))['total']
        )
        contexte['encaisse_annee'] = encaisse or 0
        contexte['total_paiements'] = Paiement.objects.filter(annee_scolaire=annee).count()

    # --- Restriction enseignant : ses classes et ses élèves ---
    if request.user.est_enseignant and hasattr(request.user, 'enseignant'):
        enseignant = request.user.enseignant
        mes_classes = enseignant.classes
        if annee:
            mes_classes = mes_classes.filter(anne_scolaire=annee)
        contexte['mes_classes'] = mes_classes
        contexte['mes_enseignements'] = (
            enseignant.enseignements.filter(classe__anne_scolaire=annee)
            .select_related('classe', 'matiere')
            if annee else enseignant.enseignements.select_related('classe', 'matiere')
        )
        contexte['mes_eleves'] = Eleve.objects.filter(
            inscriptions__classe__in=mes_classes,
            inscriptions__statut='active',
        ).distinct().count()

    return render(request, 'core/dashboard.html', contexte)