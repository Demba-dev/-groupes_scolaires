"""Filtres de templates utilitaires pour l'interface."""

from django import template

register = template.Library()


@register.filter(name='add_css')
def add_css(field, css):
    """Ajoute une classe CSS au widget d'un champ de formulaire."""
    classes = field.field.widget.attrs.get('class', '')
    if css not in classes.split():
        field.field.widget.attrs['class'] = f'{classes} {css}'.strip()
    return field


@register.filter(name='montant')
def montant(value):
    """Formate un montant en FCFA : 12 500 FCFA."""
    try:
        return f"{int(value):,}".replace(',', ' ') + " FCFA"
    except (TypeError, ValueError):
        return ''