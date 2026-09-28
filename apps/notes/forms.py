"""Formulaires des évaluations."""

from django import forms

from apps.scolarite.models import Classe, Matiere

from .models import Evaluation


class DateInput(forms.DateInput):
    input_type = 'date'


def classes_autorisees(user, annee=None):
    """Classes accessibles selon le rôle :
    - direction : toutes ;
    - enseignant : ses classes (titulaire + affectations).
    """
    from apps.accounts.models import ROLE_DIRECTION

    qs = Classe.objects.select_related('anne_scolaire', 'niveau').order_by(
        '-anne_scolaire__date_debut', 'niveau__ordre', 'section'
    )
    if annee:
        qs = qs.filter(anne_scolaire_id=annee)
    if user.role == ROLE_DIRECTION:
        return qs
    enseignant = getattr(user, 'enseignant', None)
    return enseignant.classes if enseignant else Classe.objects.none()


def matieres_autorisees(user, classe=None):
    if user.role == 'direction':
        return Matiere.objects.all()
    enseignant = getattr(user, 'enseignant', None)
    if not enseignant:
        return Matiere.objects.none()
    qs = enseignant.enseignements.select_related('matiere')
    if classe:
        qs = qs.filter(classe=classe)
    ids = qs.values_list('matiere_id', flat=True)
    return Matiere.objects.filter(id__in=ids)


class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = [
            'classe', 'matiere', 'annee_scolaire', 'type_evaluation',
            'periode', 'titre', 'date', 'bareme',
        ]
        widgets = {
            'date': DateInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields['classe'].queryset = classes_autorisees(user)
            self.fields['matiere'].queryset = matieres_autorisees(user)
        annees = self.fields['annee_scolaire'].queryset
        self.fields['annee_scolaire'].queryset = annees.order_by('-date_debut')

    def clean(self):
        donnees = super().clean()
        user = self.user
        classe = donnees.get('classe')
        matiere = donnees.get('matiere')
        if (
            user
            and user.is_authenticated
            and user.role != 'direction'
            and classe
            and matiere
            and matiere not in matieres_autorisees(user, classe)
        ):
            self.add_error(
                'matiere',
                "Vous ne pouvez saisir une évaluation que dans une matière que vous enseignez "
                "dans cette classe.",
            )
        return donnees