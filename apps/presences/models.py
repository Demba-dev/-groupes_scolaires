"""Présences, absences et retards."""

from django.conf import settings
from django.db import models

STATUT_PRESENCE_CHOICES = [
    ('present', 'Présent'),
    ('absent', 'Absent'),
    ('retard', 'Retard'),
]


class Presence(models.Model):
    """Pointage d'un élève pour une date donnée."""

    eleve = models.ForeignKey(
        'eleves.Eleve',
        verbose_name='Élève',
        on_delete=models.CASCADE,
        related_name='presences',
    )
    classe = models.ForeignKey(
        'scolarite.Classe',
        verbose_name='Classe',
        on_delete=models.CASCADE,
        related_name='presences',
    )
    date = models.DateField('Date')
    statut = models.CharField('Statut', max_length=10, choices=STATUT_PRESENCE_CHOICES)
    justifie = models.BooleanField('Absence justifiée', default=False)
    motif = models.CharField('Motif', max_length=255, blank=True)
    enregistre_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Enregistré par',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
        ordering = ['-date', 'eleve__nom']
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'date'],
                name='unique_eleve_date',
            )
        ]

    def __str__(self):
        return f"{self.eleve.nom_complet} — {self.get_statut_display()} ({self.date})"