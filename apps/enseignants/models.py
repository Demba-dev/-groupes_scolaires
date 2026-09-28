"""Enseignants de l'établissement.

Chaque enseignant peut être lié à un compte utilisateur (rôle « enseignant »)
afin d'accéder à l'application. Ses classes et matières sont déterminées par
les affectations « Enseignement » et par les postes de titulaire.
"""

from django.conf import settings
from django.db import models

SEXE_CHOICES = [
    ('M', 'Masculin'),
    ('F', 'Féminin'),
]


class Enseignant(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name='Compte utilisateur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enseignant',
    )
    matricule = models.CharField('Matricule', max_length=30, unique=True)
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100, blank=True)
    sexe = models.CharField('Sexe', max_length=1, choices=SEXE_CHOICES, default='M')
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    adresse = models.CharField('Adresse', max_length=255, blank=True)
    specialite = models.CharField('Spécialité', max_length=100, blank=True)
    actif = models.BooleanField('En activité', default=True)

    class Meta:
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return self.nom_complet

    @property
    def nom_complet(self) -> str:
        return f"{self.nom} {self.prenom}".strip()

    @property
    def classes(self):
        """Classes affectées (titulaire ou via un enseignement)."""
        ids = set(self.classes_dirigees.values_list('id', flat=True))
        ids.update(self.enseignements.values_list('classe_id', flat=True))
        from apps.scolarite.models import Classe
        return Classe.objects.filter(id__in=ids)

    @property
    def matieres(self):
        return self.enseignements.select_related('matiere').all()