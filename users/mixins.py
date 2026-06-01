from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

from .models import User


class ApprovedUserRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.can_access_panel:
            messages.warning(request, "Sua conta ainda nao esta liberada para acesso.")
            return redirect("logout")
        if request.user.is_authenticated and not request.user.has_condominium_access:
            messages.warning(request, "Voce nao tem acesso autorizado a nenhum condominio.")
            return redirect("logout")
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(ApprovedUserRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_gcondid_admin


class StaffRequiredMixin(ApprovedUserRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.access_level in {User.AccessLevel.ADMIN, User.AccessLevel.FUNCIONARIO} or self.request.user.is_superuser

