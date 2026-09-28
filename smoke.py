"""Test de fumée : parcourt toutes les pages en tant que direction puis enseignant."""
import sys

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client

settings.ALLOWED_HOSTS.append('testserver')

User = get_user_model()

admin = User.objects.get(username='admin')
prof = User.objects.get(username='prof')

from apps.scolarite.models import AnneeScolaire, Classe
from apps.notes.models import Evaluation, Bulletin
from apps.finance.models import Paiement
from apps.eleves.models import Eleve

annee_id = AnneeScolaire.objects.first().pk
classe = Classe.objects.first()
if not Bulletin.objects.exists():
    from apps.notes import services as services
    services.generer_bulletins_classe(classe, classe.anne_scolaire, 't1')
evaluation = Evaluation.objects.first()
bulletin = Bulletin.objects.first()
paiement = Paiement.objects.first()
eleve = Eleve.objects.first()

PAGES_DIRECTION = [
    '/',
    '/comptes/utilisateurs/',
    '/comptes/utilisateurs/nouveau/',
    f'/comptes/utilisateurs/{admin.pk}/modifier/',
    '/scolarite/annees/',
    '/scolarite/annees/nouvelle/',
    f'/scolarite/annees/{annee_id}/modifier/',
    '/scolarite/classes/',
    '/scolarite/classes/nouvelle/',
    f'/scolarite/classes/{classe.pk}/',
    f'/scolarite/classes/{classe.pk}/modifier/',
    '/scolarite/matieres/',
    '/scolarite/matieres/nouvelle/',
    '/scolarite/enseignements/',
    '/scolarite/enseignements/nouveau/',
    '/eleves/',
    '/eleves/nouveau/',
    f'/eleves/{eleve.pk}/',
    f'/eleves/{eleve.pk}/modifier/',
    '/eleves/inscriptions/',
    '/eleves/inscriptions/nouvelle/',
    '/eleves/tuteurs/',
    '/eleves/tuteurs/nouveau/',
    '/enseignants/',
    '/enseignants/nouveau/',
    f'/enseignants/{prof.enseignant.pk}/',
    f'/enseignants/{prof.enseignant.pk}/modifier/',
    '/notes/evaluations/',
    '/notes/evaluations/nouvelle/',
    f'/notes/evaluations/{evaluation.pk}/',
    f'/notes/evaluations/{evaluation.pk}/modifier/',
    f'/notes/evaluations/{evaluation.pk}/notes/',
    '/notes/bulletins/',
    f'/notes/bulletins/{bulletin.pk}/',
    f'/notes/classement/{classe.pk}/t1/',
    '/presences/appel/',
    '/presences/',
    '/finance/frais/',
    '/finance/frais/nouveau/',
    '/finance/paiements/',
    '/finance/paiements/nouveau/',
    f'/finance/paiements/{paiement.pk}/',
    f'/finance/paiements/{paiement.pk}/modifier/',
    '/finance/reste-a-payer/',
    f'/scolarite/classes/{classe.pk}/liste-imprimer/',
    f'/eleves/{eleve.pk}/certificat/',
]

PAGES_PROF = [
    '/',
    '/notes/evaluations/',
    '/notes/bulletins/',
    f'/scolarite/classes/{classe.pk}/',
]

PROF_BLOQUEES = ['/comptes/utilisateurs/', '/finance/paiements/']


def run(client, pages, nom):
    ok = 0
    for url in pages:
        r = client.get(url)
        if r.status_code == 200:
            ok += 1
        else:
            print(f'  [{r.status_code}] {url}')
    print(f'{nom} : {ok}/{len(pages)} OK')
    return ok == len(pages)


c = Client()
assert c.login(username='admin', password='admin123')
dir_ok = run(c, PAGES_DIRECTION, 'Direction')

c2 = Client()
assert c2.login(username='prof', password='prof123')
prof_ok = run(c2, PAGES_PROF, 'Enseignant')

bloque_ok = True
for url in PROF_BLOQUEES:
    r = c2.get(url)
    if r.status_code != 403:
        print(f'  [403 attendu] {url} -> {r.status_code}')
        bloque_ok = False
print(f'Accès bloqués (enseignant) : {"OK" if bloque_ok else "ÉCHEC"}')

# --- Accès anonyme ---
anonyme = Client()
r_login = anonyme.get('/comptes/connexion/')
r_dash = anonyme.get('/')
anonyme_ok = r_login.status_code == 200 and r_dash.status_code == 302
print(f'Accès anonyme (login 200 / dashboard 302) : {"OK" if anonyme_ok else "ÉCHEC"}')

sys.exit(0 if (dir_ok and prof_ok and bloque_ok and anonyme_ok) else 1)