"""Élèves, parents/tuteurs et inscriptions.

L'inscription est la pierre angulaire : elle lie un élève à une classe
pour une année scolaire et constitue l'historique scolaire de l'élève.
"""

from django.db import models
from django.utils import timezone

SEXE_CHOICES = [
    ('M', 'Masculin'),
    ('F', 'Féminin'),
]

LIEN_CHOICES = [
    ('pere', 'Père'),
    ('mere', 'Mère'),
    ('tuteur', 'Tuteur / Tutrice'),
    ('autre', 'Autre'),
]

STATUT_ELEVE_CHOICES = [
    ('actif', 'Actif'),
    ('transfere', 'Transféré'),
    ('exclu', 'Exclu'),
    ('abandon', 'En abandon'),
    ('diplome', 'Diplômé'),
    ('archive', 'Archivé'),
]

TYPE_INSCRIPTION_CHOICES = [
    ('inscription', 'Nouvelle inscription'),
    ('reinscription', 'Réinscription'),
]

STATUT_INSCRIPTION_CHOICES = [
    ('active', 'Active'),
    ('cloturee', 'Clôturée'),
]


class ParentTuteur(models.Model):
    """Parent ou tuteur d'un ou plusieurs élèves."""

    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100, blank=True)
    telephone = models.CharField('Téléphone', max_length=20)
    adresse = models.CharField('Adresse', max_length=255, blank=True)
    profession = models.CharField('Profession', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Parent / Tuteur'
        verbose_name_plural = 'Parents / Tuteurs'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom} {self.prenom}".strip()

    @property
    def nom_complet(self) -> str:
        return f"{self.nom} {self.prenom}".strip()


class Eleve(models.Model):
    matricule = models.CharField('Matricule', max_length=30, unique=True)
    nom = models.CharField('Nom', max_length=100)
    prenom = models.CharField('Prénom', max_length=100)
    date_naissance = models.DateField('Date de naissance', null=True, blank=True)
    lieu_naissance = models.CharField('Lieu de naissance', max_length=100, blank=True)
    sexe = models.CharField('Sexe', max_length=1, choices=SEXE_CHOICES, default='M')
    adresse = models.CharField('Adresse', max_length=255, blank=True)
    photo = models.ImageField(
        'Photo', upload_to='photos_eleves/', null=True, blank=True
    )
    tuteur = models.ForeignKey(
        ParentTuteur,
        verbose_name='Parent / Tuteur',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eleves',
    )
    lien_parent = models.CharField(
        'Lien avec le tuteur',
        max_length=10,
        choices=LIEN_CHOICES,
        blank=True,
        default='',
    )
    telephone_tuteur = models.CharField('Téléphone du parent/tuteur', max_length=20, blank=True)
    statut = models.CharField(
        'Statut', max_length=20, choices=STATUT_ELEVE_CHOICES, default='actif'
    )
    cree_le = models.DateTimeField('Créé le', auto_now_add=True)
    modifie_le = models.DateTimeField('Modifié le', auto_now=True)

    class Meta:
        verbose_name = 'Élève'
        verbose_name_plural = 'Élèves'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.matricule} — {self.nom_complet}"

    @property
    def nom_complet(self) -> str:
        return f"{self.nom} {self.prenom}".strip()

    @property
    def inscription_active(self):
        return self.inscriptions.filter(statut='active', annee_scolaire__en_cours=True).first()

    @property
    def classe_actuelle(self):
        ins = self.inscription_active
        return ins.classe if ins else None

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('eleves:eleve_detail', args=[self.pk])


class Inscription(models.Model):
    """Inscription / réinscription d'un élève dans une classe pour une année."""

    eleve = models.ForeignKey(
        Eleve,
        verbose_name='Élève',
        on_delete=models.CASCADE,
        related_name='inscriptions',
    )
    annee_scolaire = models.ForeignKey(
        'scolarite.AnneeScolaire',
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='inscriptions',
    )
    classe = models.ForeignKey(
        'scolarite.Classe',
        verbose_name='Classe',
        on_delete=models.CASCADE,
        related_name='inscriptions',
    )
    type_inscription = models.CharField(
        'Type d\'inscription',
        max_length=20,
        choices=TYPE_INSCRIPTION_CHOICES,
        default='inscription',
    )
    statut = models.CharField(
        'Statut', max_length=20, choices=STATUT_INSCRIPTION_CHOICES, default='active'
    )
    date_inscription = models.DateField('Date d\'inscription', default=timezone.localdate)

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        ordering = ['-annee_scolaire__date_debut', 'classe']
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'annee_scolaire'],
                name='unique_eleve_annee_scolaire',
            )
        ]

    def __str__(self):
        return f"{self.eleve.nom_complet} → {self.classe.nom} ({self.annee_scolaire})"

    @property
    def cycle_libelle(self) -> str:
        return self.classe.cycle_libelle