"""Utilisateurs et rôles.

Pour la première version, deux rôles seulement :
- « direction » : administrateur / Direction (mêmes permissions)
- « enseignant » : accès limité à ses classes et matières.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_DIRECTION = 'direction'
ROLE_ENSEIGNANT = 'enseignant'

ROLE_CHOICES = [
    (ROLE_DIRECTION, "Direction / Administration"),
    (ROLE_ENSEIGNANT, "Enseignant"),
]


class User(AbstractUser):
    """Utilisateur de l'application avec un rôle métier."""

    role = models.CharField(
        'Rôle',
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_DIRECTION,
    )
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    is_active = models.BooleanField('Actif', default=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def est_direction(self):
        return self.role == ROLE_DIRECTION

    @property
    def est_enseignant(self):
        return self.role == ROLE_ENSEIGNANT