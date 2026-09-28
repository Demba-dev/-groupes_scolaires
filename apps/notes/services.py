"""Moteur de calcul des résultats scolaires.

Toute la logique souple (moyennes, points, classement, décisions) vit ici
afin de pouvoir être adaptée aux règles de l'établissement sans toucher
aux vues ni aux modèles.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

from django.conf import settings

from .models import Bulletin, DECISION_CHOICES

NOTES_PASSAGE = Decimal('10.00')   # moyenne minimale pour obtenir une année
RANG_PASSAGE_PREMIER = Decimal('10.00')  # seuil de passage 1er cycle


@dataclass
class LigneMatiere:
    """Résultat d'un élève dans une matière pour une période donnée."""

    matiere: str
    coefficient: int = 1
    notes: list = field(default_factory=list)
    moyenne: Decimal | None = None

    def calculer_moyenne(self) -> None:
        # Les notes SONT déjà ramenées sur le barème de référence (NOTE_BASE).
        if not self.notes:
            self.moyenne = None
            return
        total = sum(self.notes)
        self.moyenne = Decimal(f"{(total / len(self.notes)):.2f}")

    @property
    def points(self) -> Decimal:
        """Pondération de la matière = moyenne × coefficient."""
        return (self.moyenne * self.coefficient) if self.moyenne is not None else Decimal('0')


def moyenne_ponderee(lignes: list[LigneMatiere]) -> Decimal | None:
    """Moyenne générale = somme des points / somme des coefficients."""
    lignes = [l for l in lignes if l.moyenne is not None]
    if not lignes:
        return None
    somme_points = sum(l.points for l in lignes)
    somme_coeff = sum(l.coefficient for l in lignes)
    if somme_coeff == 0:
        return None
    return (somme_points / somme_coeff).quantize(Decimal('0.01'))


def notes_par_matiere(eleve, classe, annee_scolaire, periode, base: int | None = None):
    """Indexe les notes de l'élève par matière, ramenées sur le barème de référence.

    Retourne : dict {matiere_id: (nom_matiere, coefficient, [notes sur 20])}
    """
    base = base or settings.NOTE_BASE
    evaluations = (
        eleve.notes.select_related('evaluation', 'evaluation__matiere')
        .filter(
            evaluation__classe=classe,
            evaluation__annee_scolaire=annee_scolaire,
            evaluation__periode=periode,
        )
        .order_by('evaluation__matiere__nom', 'evaluation__date')
    )
    index = defaultdict(lambda: [None, 0, []])   # matiere_id -> [nom, coeff, notes]
    for note in evaluations:
        ev = note.evaluation
        valeur20 = (
            float(note.valeur) * base / float(ev.bareme) if ev.bareme else 0.0
        )
        index[ev.matiere_id][0] = ev.matiere.nom
        index[ev.matiere_id][1] = ev.coefficient
        index[ev.matiere_id][2].append(valeur20)
    return index


def lignes_matiere(eleve, classe, annee_scolaire, periode, base: int | None = None) -> list[LigneMatiere]:
    """Construit les lignes matière (avec moyennes calculées) de l'élève."""
    index = notes_par_matiere(eleve, classe, annee_scolaire, periode, base)
    lignes: list[LigneMatiere] = []
    for matiere_id, (nom, coeff, notes) in sorted(index.items(), key=lambda x: x[1][0]):
        ligne = LigneMatiere(matiere=nom, coefficient=coeff, notes=notes)
        ligne.calculer_moyenne()
        lignes.append(ligne)
    return lignes


def moyenne_eleve(eleve, classe, annee_scolaire, periode, base: int | None = None) -> Decimal | None:
    return moyenne_ponderee(lignes_matiere(eleve, classe, annee_scolaire, periode, base))


def classement_classe(classe, annee_scolaire, periode, base: int | None = None):
    """Retourne la liste (non triée) des (élève, moyenne, ligne_matieres, rang)."""
    resultats = []
    inscriptions = classe.inscriptions.filter(
        statut='active', annee_scolaire=annee_scolaire
    ).select_related('eleve')
    for ins in inscriptions:
        lignes = lignes_matiere(ins.eleve, classe, annee_scolaire, periode, base)
        moyenne = moyenne_ponderee(lignes)
        resultats.append((ins.eleve, moyenne, lignes))
    resultats.sort(key=lambda x: (x[1] is None, -(x[1] or Decimal('0'))))
    return resultats


def attribuer_rangs(resultats: list) -> None:
    """Attribue le rang (1 = meilleur) de façon stable, en gérant les ex æquo."""
    rang = 0
    previous: Decimal | None = None
    previous_rank = 0
    for i, (eleve, moyenne, lignes) in enumerate(resultats, start=1):
        if moyenne is None:
            rang = 0
            previous = None
            previous_rank = 0
        elif moyenne != previous:
            rang = i
            previous = moyenne
            previous_rank = rang
        else:
            rang = previous_rank
        yield (eleve, moyenne, lignes, rang)


def decision_eleve(eleve, moyenne: Decimal | None) -> str:
    if moyenne is None:
        return ''
    if moyenne >= NOTES_PASSAGE:
        return 'admise' if eleve.sexe == 'F' else 'admis'
    return 'redouble'


def generer_bulletin(eleve, classe, annee_scolaire, periode, base: int | None = None) -> Bulletin:
    """(Re)génère et enregistre le bulletin d'un élève pour une période/an."""
    lignes = lignes_matiere(eleve, classe, annee_scolaire, periode, base)
    moyenne = moyenne_ponderee(lignes)
    resultats = classement_classe(classe, annee_scolaire, periode, base)
    rang = next(
        (r for (e, m, li, r) in attribuer_rangs(resultats) if e.id == eleve.id), None
    )
    bulletin, _ = Bulletin.objects.update_or_create(
        eleve=eleve,
        annee_scolaire=annee_scolaire,
        periode=periode,
        defaults={
            'classe': classe,
            'moyenne_generale': moyenne,
            'rang': rang,
            'effectif_classe': len(resultats),
            'decision': decision_eleve(eleve, moyenne),
        },
    )
    return bulletin


def generer_bulletins_classe(classe, annee_scolaire, periode, base: int | None = None) -> int:
    """Régénère les bulletins de toute une classe pour une période."""
    count = 0
    for ins in classe.inscriptions.filter(statut='active', annee_scolaire=annee_scolaire):
        generer_bulletin(ins.eleve, classe, annee_scolaire, periode, base)
        count += 1
    return count