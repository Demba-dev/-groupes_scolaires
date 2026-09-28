"""Données de base : niveaux 1ère-9ème et matières de l'école fondamentale."""

from django.core.management.base import BaseCommand

from apps.scolarite.models import Matiere, Niveau

LIBELLES_NIVEAUX = {
    1: '1ère année',
    2: '2ème année',
    3: '3ème année',
    4: '4ème année',
    5: '5ème année',
    6: '6ème année',
    7: '7ème année',
    8: '8ème année',
    9: '9ème année',
}

MATIERES = [
    ('FR', 'Français', 2),
    ('MATH', 'Mathématiques', 2),
    ('HG', 'Histoire-Géographie', 1),
    ('SO', 'Sciences d\'observation', 1),
    ('ECM', 'Éducation civique et morale', 1),
    ('LN', 'Langues nationales', 1),
    ('ANG', 'Anglais', 1),
    ('EPS', 'Éducation physique et sportive', 1),
    ('EA', 'Éducation artistique', 1),
]


class Command(BaseCommand):
    help = "Initialise les niveaux (1ère à 9ème) et les matières de base."

    def handle(self, *args, **options):
        for ordre, libelle in LIBELLES_NIVEAUX.items():
            obj, created = Niveau.objects.get_or_create(
                ordre=ordre,
                defaults={'libelle': libelle},
            )
            if not created and obj.libelle != libelle:
                obj.libelle = libelle
                obj.save(update_fields=['libelle'])

        for code, nom, coefficient in MATIERES:
            Matiere.objects.get_or_create(
                code=code,
                defaults={'nom': nom, 'coefficient': coefficient},
            )

        self.stdout.write(self.style.SUCCESS(
            f"Niveaux : {Niveau.objects.count()} · Matières : {Matiere.objects.count()}"
        ))