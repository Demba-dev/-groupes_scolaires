"""Organisation pédagogique : années scolaires, niveaux, classes, matières.

Le cycle (1er : 1ère-6ème / 2ème : 7ème-9ème) est déduit automatiquement
du niveau concerné.
"""

from django.conf import settings
from django.db import models

CYCLE_PREMIER = 'premier'
CYCLE_DEUXIEME = 'deuxieme'

CYCLE_CHOICES = [
    (CYCLE_PREMIER, "1er cycle (1ère – 6ème année)"),
    (CYCLE_DEUXIEME, "2ème cycle (7ème – 9ème année)"),
]

# Ordre du niveau → cycle
PREMIER_CYCLE_MAX = 6


def cycle_du_niveau(ordre: int) -> str:
    """Déduit le cycle pédagogique d'un niveau (1ère à 9ème année)."""
    return CYCLE_PREMIER if ordre <= PREMIER_CYCLE_MAX else CYCLE_DEUXIEME


class AnneeScolaire(models.Model):
    """Année scolaire, ex. « 2025-2026 ». Toutes les données sont liées à cette année."""

    libelle = models.CharField('Libellé', max_length=20, unique=True)
    date_debut = models.DateField('Date de début')
    date_fin = models.DateField('Date de fin')
    en_cours = models.BooleanField('Année en cours', default=False)
    cloturee = models.BooleanField('Clôturée', default=False)

    class Meta:
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-date_debut']

    def __str__(self):
        return self.libelle


class Niveau(models.Model):
    """Niveau d'enseignement : 1ère jusqu'à 9ème année."""

    ordre = models.PositiveSmallIntegerField('Ordre', unique=True)
    libelle = models.CharField(
        'Libellé',
        max_length=60,
        help_text="Ex. « 1ère année », « 6ème année », « 9ème année »",
    )

    class Meta:
        verbose_name = 'Niveau'
        verbose_name_plural = 'Niveaux'
        ordering = ['ordre']

    def __str__(self):
        return self.libelle

    @property
    def cycle(self) -> str:
        return cycle_du_niveau(self.ordre)

    @property
    def cycle_libelle(self) -> str:
        return dict(CYCLE_CHOICES)[self.cycle] if self.cycle else ''


class Classe(models.Model):
    """Une classe pour une année scolaire donnée.

    Ex. « 5ème A » en 2025-2026. Une même classe d'une année à l'autre est
    un enregistrement distinct (historique conservé).
    """

    anne_scolaire = models.ForeignKey(
        AnneeScolaire,
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='classes',
    )
    niveau = models.ForeignKey(
        Niveau,
        verbose_name='Niveau',
        on_delete=models.PROTECT,
        related_name='classes',
    )
    section = models.CharField(
        'Section',
        max_length=10,
        blank=True,
        default='',
        help_text='Ex. « A », « B » … Laisse vide s\'il n\'y a qu\'une classe par niveau.',
    )
    enseignant_titulaire = models.ForeignKey(
        'enseignants.Enseignant',
        verbose_name='Enseignant titulaire',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_dirigees',
    )
    capacite_max = models.PositiveSmallIntegerField('Capacité max', default=60)
    active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        ordering = ['anne_scolaire', 'niveau__ordre', 'section']
        constraints = [
            models.UniqueConstraint(
                fields=['anne_scolaire', 'niveau', 'section'],
                name='unique_classe_annee_niveau_section',
            )
        ]

    def __str__(self):
        return self.nom

    @property
    def nom(self) -> str:
        section = self.section.strip()
        return f"{self.niveau.libelle} {section}".strip() if section else self.niveau.libelle

    @property
    def cycle(self) -> str:
        return self.niveau.cycle

    @property
    def cycle_libelle(self) -> str:
        return self.niveau.cycle_libelle

    @property
    def effectif(self) -> int:
        return self.inscriptions.filter(statut='active').count()


class Matiere(models.Model):
    """Matière enseignée (Français, Mathématiques, …)."""

    nom = models.CharField('Nom', max_length=100, unique=True)
    code = models.CharField('Code', max_length=10, unique=True)
    coefficient = models.PositiveSmallIntegerField('Coefficient', default=1)
    description = models.TextField('Description', blank=True)

    class Meta:
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Enseignement(models.Model):
    """Affectation d'un enseignant à une classe pour une matière.

    C'est l'« enseignant responsable » de la matière dans cette classe,
    avec possibilité d'ajuster le coefficient et l'horaire hebdomadaire.
    """

    classe = models.ForeignKey(
        Classe,
        verbose_name='Classe',
        on_delete=models.CASCADE,
        related_name='enseignements',
    )
    matiere = models.ForeignKey(
        Matiere,
        verbose_name='Matière',
        on_delete=models.CASCADE,
        related_name='enseignements',
    )
    enseignant = models.ForeignKey(
        'enseignants.Enseignant',
        verbose_name='Enseignant',
        on_delete=models.CASCADE,
        related_name='enseignements',
    )
    coefficient = models.PositiveSmallIntegerField(
        'Coefficient',
        null=True,
        blank=True,
        help_text='Laisse vide pour reprendre le coefficient de la matière.',
    )
    horaire_hebdomadaire = models.PositiveSmallIntegerField(
        'Horaire hebdomadaire (h)',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Enseignement'
        verbose_name_plural = 'Enseignements'
        ordering = ['classe', 'matiere']
        constraints = [
            models.UniqueConstraint(
                fields=['classe', 'matiere'],
                name='unique_classe_matiere',
            )
        ]

    def __str__(self):
        return f"{self.classe} — {self.matiere.nom}"

    @property
    def coefficient_effectif(self) -> int:
        return self.coefficient or self.matiere.coefficient


def niveau_par_ordre(ordre: int) -> Niveau | None:
    try:
        return Niveau.objects.get(ordre=ordre)
    except Niveau.DoesNotExist:
        return None