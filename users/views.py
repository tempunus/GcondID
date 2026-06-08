from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.views import View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from permissoes.mixins import PermissaoRequiredMixin

from .forms import AdminUserCreateForm, EmailAuthenticationForm, UserApprovalForm
from .mixins import AdminRequiredMixin
from .models import User


class CustomLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "registration/login.html"


class SignUpView(View):
    def get(self, request, *args, **kwargs):
        messages.info(request, "Novos usuarios devem ser criados por um administrador.")
        return redirect("login")

    def post(self, request, *args, **kwargs):
        messages.info(request, "Novos usuarios devem ser criados por um administrador.")
        return redirect("login")


class UserListView(PermissaoRequiredMixin, AdminRequiredMixin, ListView):
    permissao_required = "visualizar_usuarios"
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.order_by("is_approved", "first_name", "email")


class UserCreateView(PermissaoRequiredMixin, AdminRequiredMixin, CreateView):
    permissao_required = "cadastrar_usuarios"
    model = User
    form_class = AdminUserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario criado.")
        return super().form_valid(form)


class UserUpdateView(PermissaoRequiredMixin, AdminRequiredMixin, UpdateView):
    permissao_required = "editar_usuarios"
    model = User
    form_class = UserApprovalForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario atualizado.")
        return super().form_valid(form)


class UserDeleteView(PermissaoRequiredMixin, AdminRequiredMixin, DeleteView):
    permissao_required = "excluir_usuarios"
    model = User
    template_name = "users/user_confirm_delete.html"
    success_url = reverse_lazy("users:list")

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.pk == request.user.pk:
            messages.warning(request, "Voce nao pode excluir sua propria conta enquanto esta logado.")
            return redirect("users:list")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Nao foi possivel excluir este usuario porque ele possui registros vinculados, como chamados abertos. Bloqueie ou desative a conta para impedir novos acessos.",
            )
            return redirect("users:list")
        messages.success(self.request, "Usuario excluido.")
        return response
