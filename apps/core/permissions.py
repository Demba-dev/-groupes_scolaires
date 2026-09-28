"""Décorateurs et mixins de contrôle d'accès par rôle.

Usage :
    @login_required
    @role_required('direction')
    def ma_vue(request): ...

    class MaVue(RoleRequiredMixin, TemplateView):
        required_role = 'direction'
"""

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.utils.decorators import method_decorator

from apps.accounts.models import ROLE_DIRECTION, ROLE_ENSEIGNANT


def role_required(role):
    """Vue fonction → seuls les utilisateurs ayant le rôle peuvent accéder."""

    def decorateur(view_func):
        @login_required
        def _wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.role != role and not request.user.role == ROLE_DIRECTION:
                # Seule la direction peut tout faire ; sinon le rôle doit correspondre.
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapper

    return decorateur


def direction_required(view_func):
    """Réserve une vue à la Direction / Administration."""
    return role_required(ROLE_DIRECTION)(view_func)


def enseignant_required(view_func):
    """Réserve une vue aux enseignants (et à la direction)."""
    from apps.accounts.models import ROLE_ENSEIGNANT

    return role_required(ROLE_ENSEIGNANT)(view_func)


class RoleRequiredMixin:
    """MixIn pour les vues par classes.

    - `roles` : liste des rôles autorisés (la direction est toujours autorisée).
    Par défaut : réservé à la direction.
    """

    roles = None  # None → direction uniquement

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        autorise = self.request.user.role == ROLE_DIRECTION
        if not autorise and self.roles:
            autorise = self.request.user.role in self.roles
        if not autorise:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class DirectionRequiredMixin(RoleRequiredMixin):
    roles = None


class EnseignantAccessMixin(RoleRequiredMixin):
    """Accès direction + enseignant."""

    roles = [ROLE_ENSEIGNANT]