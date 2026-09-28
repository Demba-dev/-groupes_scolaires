"""Évaluations, notes et bulletins.

La logique de calcul (moyennes, classement, décisions) est centralisée
dans `apps.notes.services` afin de pouvoir être adaptée aux règles de
l'établissement.
"""

from django.conf import settings
from django.db import models

TYPE_EVALUATION_CHOICES = [
    ('devoir', 'Devoir / contrôle'),
    ('composition', 'Composition'),
    ('examen', 'Examen'),
    ('rattrapage', 'Rattrapage'),
]

PERIODE_CHOICES = [
    ('t1', '1er trimestre'),
    ('t2', '2ème trimestre'),
    ('t3', '3ème trimestre'),
    ('annuel', 'Annuel'),
]

DECISION_CHOICES = [
    ('admise', 'Admise'),
    ('admis', 'Admis'),
    ('redouble', 'Redouble'),
    ('non_prononcee', 'Non prononcée'),
]


class Evaluation(models.Model):
    """Une évaluation pour une classe et une matière (devoir, composition…)."""

    classe = models.ForeignKey(
        'scolarite.Classe',
        verbose_name='Classe',
        on_delete=models.CASCADE,
        related_name='evaluations',
    )
    matiere = models.ForeignKey(
        'scolarite.Matiere',
        verbose_name='Matière',
        on_delete=models.CASCADE,
        related_name='evaluations',
    )
    annee_scolaire = models.ForeignKey(
        'scolarite.AnneeScolaire',
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='evaluations',
    )
    type_evaluation = models.CharField(
        'Type', max_length=20, choices=TYPE_EVALUATION_CHOICES, default='devoir'
    )
    periode = models.CharField('Période', max_length=10, choices=PERIODE_CHOICES, default='t1')
    titre = models.CharField('Titre', max_length=120)
    date = models.DateField('Date', null=True, blank=True)
    bareme = models.DecimalField(
        'Barème', max_digits=5, decimal_places=2, default=settings.NOTE_BASE
    )
    crée_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Créé par',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        ordering = ['-date', '-id']
        constraints = [
            models.UniqueConstraint(
                fields=['classe', 'matiere', 'titre'],
                name='unique_classe_matiere_titre',
            )
        ]

    def __str__(self):
        return f"{self.titre} — {self.matiere.nom} ({self.classe.nom})"

    @property
    def coefficient(self) -> int:
        enseignement = self.classe.enseignements.filter(matiere=self.matiere).first()
        return enseignement.coefficient_effectif if enseignement else self.matiere.coefficient

    @property
    def eleves_notes(self) -> int:
        return self.notes.count()


class Note(models.Model):
    """Note d'un élève pour une évaluation."""

    evaluation = models.ForeignKey(
        Evaluation,
        verbose_name='Évaluation',
        on_delete=models.CASCADE,
        related_name='notes',
    )
    eleve = models.ForeignKey(
        'eleves.Eleve',
        verbose_name='Élève',
        on_delete=models.CASCADE,
        related_name='notes',
    )
    valeur = models.DecimalField(
        'Note', max_digits=5, decimal_places=2,
        help_text=f'Note sur le barème de l\'évaluation (par défaut /{settings.NOTE_BASE}).',
    )

    class Meta:
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['eleve__nom', 'eleve__prenom']
        constraints = [
            models.UniqueConstraint(
                fields=['evaluation', 'eleve'],
                name='unique_evaluation_eleve',
            )
        ]

    def __str__(self):
        return f"{self.eleve.nom_complet} — {self.valeur}/{self.evaluation.bareme}"

    @property
    def valeur_sur_vingt(self, base: int | None = None) -> float:
        """Note ramenée sur le barème de référence (settings.NOTE_BASE)."""
        base = base or settings.NOTE_BASE
        if self.evaluation.bareme == 0:
            return 0.0
        return round(float(self.valeur) * base / float(self.evaluation.bareme), 2)


class Bulletin(models.Model):
    """Résultat d'un élève pour une période / l'année.

    Peut être régénéré à tout moment depuis les notes (service
    « notes.services »). Les champs stockés servent aux bulletins
    et aux décisions de fin d'année.
    """

    eleve = models.ForeignKey(
        'eleves.Eleve',
        verbose_name='Élève',
        on_delete=models.CASCADE,
        related_name='bulletins',
    )
    classe = models.ForeignKey(
        'scolarite.Classe',
        verbose_name='Classe',
        on_delete=models.CASCADE,
        related_name='bulletins',
    )
    annee_scolaire = models.ForeignKey(
        'scolarite.AnneeScolaire',
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='bulletins',
    )
    periode = models.CharField('Période', max_length=10, choices=PERIODE_CHOICES)
    moyenne_generale = models.DecimalField(
        'Moyenne générale', max_digits=5, decimal_places=2, null=True, blank=True
    )
    rang = models.PositiveIntegerField('Rang', null=True, blank=True)
    effectif_classe = models.PositiveIntegerField('Effectif de la classe', null=True, blank=True)
    appreciation = models.TextField('Appréciation', blank=True)
    decision = models.CharField(
        'Décision de fin d\'année', max_length=20, choices=DECISION_CHOICES, blank=True
    )
    cree_le = models.DateTimeField('Créé le', auto_now=True)

    class Meta:
        verbose_name = 'Bulletin'
        verbose_name_plural = 'Bulletins'
        ordering = ['annee_scolaire', 'classe', 'periode', 'rang']
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'annee_scolaire', 'periode'],
                name='unique_eleve_annee_periode',
            )
        ]

    def __str__(self):
        return f"Bulletin {self.eleve.nom_complet} — {self.periode} ({self.annee_scolaire})"