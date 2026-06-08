from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from permissoes.mixins import PermissaoRequiredMixin
from users.mixins import AdminRequiredMixin

from .forms import CondominiumForm
from .models import Condominium


class CondominiumListView(PermissaoRequiredMixin, AdminRequiredMixin, ListView):
    permissao_required = "administrar_condominio"
    model = Condominium
    template_name = "condominios/condominium_list.html"
    context_object_name = "condominiums"


class CondominiumCreateView(PermissaoRequiredMixin, AdminRequiredMixin, CreateView):
    permissao_required = "administrar_condominio"
    model = Condominium
    form_class = CondominiumForm
    template_name = "condominios/condominium_form.html"
    success_url = reverse_lazy("condominios:list")

    def form_valid(self, form):
        messages.success(self.request, "Condominio cadastrado.")
        return super().form_valid(form)


class CondominiumUpdateView(PermissaoRequiredMixin, AdminRequiredMixin, UpdateView):
    permissao_required = "administrar_condominio"
    model = Condominium
    form_class = CondominiumForm
    template_name = "condominios/condominium_form.html"
    success_url = reverse_lazy("condominios:list")

    def form_valid(self, form):
        messages.success(self.request, "Condominio atualizado.")
        return super().form_valid(form)


class CondominiumDeleteView(PermissaoRequiredMixin, AdminRequiredMixin, DeleteView):
    permissao_required = "administrar_condominio"
    model = Condominium
    template_name = "condominios/condominium_confirm_delete.html"
    success_url = reverse_lazy("condominios:list")

    def form_valid(self, form):
        messages.success(self.request, "Condominio excluido.")
        return super().form_valid(form)
