from django.contrib import messages
from django.views import View
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

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


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        return User.objects.order_by("is_approved", "first_name", "email")


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = AdminUserCreateForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario criado.")
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserApprovalForm
    template_name = "users/user_form.html"
    success_url = reverse_lazy("users:list")

    def form_valid(self, form):
        messages.success(self.request, "Usuario atualizado.")
        return super().form_valid(form)


class UserDeleteView(AdminRequiredMixin, DeleteView):
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
        messages.success(self.request, "Usuario excluido.")
        return super().form_valid(form)
