"""Données de démonstration pour tester l'application.

DANGER : à n'utiliser que sur une base vide ou de test.
"""

import random
from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import ROLE_ENSEIGNANT, User
from apps.eleves.models import Eleve, Inscription, ParentTuteur
from apps.enseignants.models import Enseignant
from apps.finance.models import Frais, Paiement
from apps.notes.models import Evaluation, Note
from apps.presences.models import Presence
from apps.scolarite.models import AnneeScolaire, Classe, Enseignement, Matiere, Niveau

PRENOMS_M = ['Moussa', 'Amadou', 'Ibrahim', 'Sékou', 'Oumar', 'Boubacar', 'Mamadou', 'Karim', 'Sidi', 'Aly']
PRENOMS_F = ['Awa', 'Fatoumata', 'Aminata', 'Mariam', 'Kadidia', 'Oumou', 'Djeneba', 'Rokia', 'Binta', 'Assetou']
NOMS = ['Traoré', 'Diarra', 'Konaté', 'Cissé', 'Keita', 'Sissoko', 'Coulibaly', 'Doumbia', 'Diallo', 'Sanogo', 'Kanté', 'Sangaré']


def _matricule(prefixe, i):
    return f"{prefixe}{2025}{i:04d}"


class Command(BaseCommand):
    help = "Crée un jeu de données de démonstration."

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Base déjà peuplée, commande ignorée.'))
            return

        # --- Année scolaire ---
        annee, _ = AnneeScolaire.objects.get_or_create(
            libelle='2025-2026',
            defaults={
                'date_debut': date(2025, 10, 1),
                'date_fin': date(2026, 6, 30),
                'en_cours': True,
            },
        )

        # --- Utilisateurs ---
        admin = User.objects.create_superuser(
            username='admin', password='admin123', role='direction'
        )
        prof_user = User.objects.create_user(
            username='prof', password='prof123', role=ROLE_ENSEIGNANT,
            first_name='Sékou', last_name='Keita',
        )

        # --- Enseignants ---
        prof1, _ = Enseignant.objects.get_or_create(
            matricule='ENS2025001',
            defaults={
                'user': prof_user, 'nom': 'Keita', 'prenom': 'Sékou',
                'sexe': 'M', 'telephone': '76000001', 'specialite': 'Mathématiques',
            },
        )
        prof2, _ = Enseignant.objects.get_or_create(
            matricule='ENS2025002',
            defaults={
                'nom': 'Diarra', 'prenom': 'Awa', 'sexe': 'F',
                'telephone': '76000002', 'specialite': 'Français',
            },
        )

        # --- Classes (1er et 2ème cycle) ---
        niveaux = {n.ordre: n for n in Niveau.objects.all()}
        classes_info = [
            (1, 'A', prof1), (4, 'A', prof2), (6, 'A', prof1),
            (7, 'A', prof2), (9, 'A', prof1),
        ]
        classes = []
        for ordre, section, titulaire in classes_info:
            classe, created = Classe.objects.get_or_create(
                anne_scolaire=annee, niveau=niveaux[ordre], section=section,
                defaults={'enseignant_titulaire': titulaire},
            )
            if created:
                for code, nombre in (('MATH', 2), ('FR', 2)):
                    matiere = Matiere.objects.get(code=code)
                    Enseignement.objects.create(
                        classe=classe, matiere=matiere,
                        enseignant=titulaire, horaire_hebdomadaire=4 if nombre == 2 else 3,
                    )
            classes.append(classe)

        # --- Parents & élèves (10 par classe) ---
        eleves = []
        for idx, classe in enumerate(classes):
            for j in range(10):
                gen = random.choice(['M', 'F'])
                prenom = random.choice(PRENOMS_M if gen == 'M' else PRENOMS_F)
                nom = random.choice(NOMS)
                tuteur, _ = ParentTuteur.objects.get_or_create(
                    nom=nom, prenom=prenom,
                    defaults={
                        'telephone': f'7{random.randint(40,99)}{random.randint(1000,9999)}',
                        'adresse': 'Bamako',
                        'profession': random.choice(['Commerçant(e)', 'Enseignant(e)', 'Ménagère', 'Fonctionnaire']),
                    },
                )
                matricule = _matricule(classe.niveau.ordre, j + 1)
                eleve, _ = Eleve.objects.get_or_create(
                    matricule=matricule,
                    defaults={
                        'nom': nom, 'prenom': prenom, 'sexe': gen,
                        'date_naissance': date(random.randint(2011, 2020), random.randint(1, 12), random.randint(1, 28)),
                        'lieu_naissance': 'Bamako',
                        'tuteur': tuteur,
                        'telephone_tuteur': tuteur.telephone,
                    },
                )
                Inscription.objects.get_or_create(
                    eleve=eleve, annee_scolaire=annee,
                    defaults={'classe': classe, 'type_inscription': 'inscription'},
                )
                eleves.append(eleve)

        # --- Frais ---
        frais_inscription, _ = Frais.objects.get_or_create(
            libelle="Droit d'inscription", annee_scolaire=annee,
            defaults={'montant': 5000},
        )
        frais_scolarite, _ = Frais.objects.get_or_create(
            libelle='Frais de scolarité', annee_scolaire=annee,
            defaults={'montant': 15000},
        )

        # --- Paiements (⅔ des élèves ont payé l'inscription) ---
        for eleve in eleves[::3][:10]:
            Paiement.objects.create(
                eleve=eleve, annee_scolaire=annee, frais=frais_inscription,
                montant=5000, mode='especes', date=date(2025, 10, 5),
                encaisse_par=admin,
            )

        # --- Évaluations & notes ---
        devoir_index = 0
        for classe in classes:
            for ens in classe.enseignements.select_related('matiere'):
                fore = Evaluation.objects.get_or_create(
                    classe=classe, matiere=ens.matiere,
                    titre=f'Devoir 1 — {ens.matiere.nom}',
                    defaults={'annee_scolaire': annee, 'periode': 't1',
                              'date': date(2025, 11, 15), 'crée_par': admin},
                )[0]
                for i in classe.inscriptions.filter(statut='active'):
                    Note.objects.get_or_create(
                        evaluation=fore, eleve=i.eleve,
                        defaults={'valeur': random.choice([8, 9, 10, 11, 12, 13, 14, 15, 16])},
                    )
                devoir_index += 1

        # --- Présences (hier, aléatoires) ---
        hier = timezone.localdate() - timezone.timedelta(days=1)
        for clique in classes[:2]:
            for ins in clique.inscriptions.filter(statut='active'):
                Presence.objects.get_or_create(
                    eleve=ins.eleve, date=hier,
                    defaults={
                        'classe': clique,
                        'statut': random.choices(
                            ['present', 'absent', 'retard'], weights=[8, 1, 1]
                        )[0],
                        'enregistre_par': prof_user,
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f'Démo créée : {len(eleves)} élèves · {len(classes)} classes · annuaire OK.'
        ))
        self.stdout.write('Compte direction : admin / admin123')
        self.stdout.write('Compte enseignant : prof / prof123')