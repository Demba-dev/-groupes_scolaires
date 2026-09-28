"""Contexte global injecté dans tous les templates."""

from apps.scolarite.models import AnneeScolaire


def global_context(request):
    """Année scolaire en cours + indicateurs d'affichage par rôle."""
    annee_courante = AnneeScolaire.objects.filter(en_cours=True).first()

    est_direction = False
    est_enseignant = False
    if request.user.is_authenticated:
        from apps.accounts.models import ROLE_DIRECTION, ROLE_ENSEIGNANT

        est_direction = request.user.role == ROLE_DIRECTION
        est_enseignant = request.user.role == ROLE_ENSEIGNANT

    return {
        'annee_scolaire_courante': annee_courante,
        'est_direction': est_direction,
        'est_enseignant': est_enseignant,
        'NOM_ECOLE': 'École Fondamentale — Groupe Scolaire',
    }