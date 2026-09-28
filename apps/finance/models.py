"""Gestion financière : frais scolaires, paiements, reçus.

Règles :
- Un « Frais » est un poste de dépense pour une année scolaire
  (droit d'inscription, frais de scolarité, …).
- Un « Paiement » est un versement d'un élève pour une année scolaire.
- Le reste à payer est calculé (service « reste_a_payer ») et non stocké.
"""

from django.conf import settings
from django.db import models
from django.db.models import Sum

MODE_PAIEMENT_CHOICES = [
    ('especes', 'Espèces'),
    ('orange_money', 'Orange Money'),
    ('momo', 'MoMo'),
    ('wave', 'Wave'),
    ('cheque', 'Chèque'),
    ('virement', 'Virement bancaire'),
]


class Frais(models.Model):
    """Poste de frais définis par l'établissement pour une année scolaire."""

    libelle = models.CharField('Libellé', max_length=120)
    montant = models.DecimalField('Montant', max_digits=10, decimal_places=2)
    annee_scolaire = models.ForeignKey(
        'scolarite.AnneeScolaire',
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='frais',
    )
    obligatoire = models.BooleanField('Obligatoire', default=True)

    class Meta:
        verbose_name = 'Frais'
        verbose_name_plural = 'Frais'
        ordering = ['annee_scolaire', 'libelle']

    def __str__(self):
        return f"{self.libelle} ({self.annee_scolaire})"


class Paiement(models.Model):
    """Versement effectué par un élève."""

    eleve = models.ForeignKey(
        'eleves.Eleve',
        verbose_name='Élève',
        on_delete=models.CASCADE,
        related_name='paiements',
    )
    annee_scolaire = models.ForeignKey(
        'scolarite.AnneeScolaire',
        verbose_name='Année scolaire',
        on_delete=models.CASCADE,
        related_name='paiements',
    )
    frais = models.ForeignKey(
        Frais,
        verbose_name='Frais',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements',
    )
    libelle = models.CharField('Objet', max_length=120, blank=True)
    montant = models.DecimalField('Montant', max_digits=10, decimal_places=2)
    mode = models.CharField(
        'Mode de paiement', max_length=20, choices=MODE_PAIEMENT_CHOICES, default='especes'
    )
    date = models.DateField('Date de paiement')
    reference = models.CharField('Référence', max_length=60, blank=True)
    recu_numero = models.CharField('N° de reçu', max_length=30, unique=True, blank=True)
    commentaire = models.CharField('Commentaire', max_length=255, blank=True)
    encaisse_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Encaissé par',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    cree_le = models.DateTimeField('Créé le', auto_now_add=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date', '-id']

    def __str__(self):
        return f"Paiement {self.eleve.nom_complet} — {self.montant} FCFA ({self.date})"

    def save(self, *args, **kwargs):
        if not self.libelle and self.frais:
            self.libelle = self.frais.libelle
        if not self.recu_numero:
            dernier_id = (
                Paiement.objects.order_by('-id').values_list('id', flat=True).first() or 0
            )
            prefixe = f"R-{self.annee_scolaire_id or ''}"
            self.recu_numero = f"{prefixe}{dernier_id + 1:04d}"
        super().save(*args, **kwargs)


def total_paye(eleve, annee_scolaire) -> int:
    total = Paiement.objects.filter(
        eleve=eleve, annee_scolaire=annee_scolaire
    ).aggregate(somme=Sum('montant'))['somme']
    return int(total or 0)


def montant_du(eleve, annee_scolaire) -> int:
    """Somme des frais obligatoires de l'année pour l'élève."""
    total = annee_scolaire.frais.filter(obligatoire=True).aggregate(somme=Sum('montant'))['somme']
    return int(total or 0)


def reste_a_payer(eleve, annee_scolaire) -> int:
    """Reste à payer = frais obligatoires - total payé (jamais négatif)."""
    reste = montant_du(eleve, annee_scolaire) - total_paye(eleve, annee_scolaire)
    return max(reste, 0)