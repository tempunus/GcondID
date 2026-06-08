from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from condominios.models import Condominium
from permissoes.mixins import PermissaoRequiredMixin
from users.mixins import ApprovedUserRequiredMixin

from .forms import StockItemForm, StockMovementForm
from .models import StockItem, StockMovement


def _authorized_condominiums(user):
    qs = Condominium.objects.filter(is_active=True).order_by("name")
    if user.is_gcondid_admin:
        return qs
    return user.authorized_condominiums.filter(is_active=True).order_by("name")


def _condominium_allowed(user, condominium_id):
    if not condominium_id:
        return True
    if user.is_gcondid_admin:
        return Condominium.objects.filter(pk=condominium_id, is_active=True).exists()
    return user.authorized_condominiums.filter(pk=condominium_id, is_active=True).exists()


def _filter_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(condominium__in=user.authorized_condominiums.filter(is_active=True))


def _filter_movements_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(item__condominium__in=user.authorized_condominiums.filter(is_active=True))


def _safe_next_url(request, fallback="estoque:list"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return next_url
    return reverse(fallback)


def _item_sector_url(item):
    url = f"{reverse('estoque:list')}?sector={item.sector}"
    if item.condominium_id:
        url += f"&condominium={item.condominium_id}"
    return url


class StockItemListView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, ListView):
    permissao_required = "acessar_estoque"
    model = StockItem
    template_name = "estoque/item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        qs = _filter_by_user_condominiums(StockItem.objects.select_related("condominium"), self.request.user)
        sector = self.request.GET.get("sector")
        condominium = self.request.GET.get("condominium")
        critical = self.request.GET.get("critical")
        if condominium:
            if not _condominium_allowed(self.request.user, condominium):
                messages.warning(self.request, "Voce nao tem autorizacao para acessar este condominio.")
                return qs.none()
            qs = qs.filter(condominium_id=condominium)
        if sector:
            qs = qs.filter(sector=sector)
        if critical:
            qs = qs.filter(current_quantity__lte=F("minimum_quantity"))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sectors"] = StockItem.Sector.choices
        context["condominiums"] = _authorized_condominiums(self.request.user)
        context["selected_sector"] = self.request.GET.get("sector", "")
        context["selected_condominium"] = self.request.GET.get("condominium", "")
        context["critical"] = self.request.GET.get("critical", "")
        movements = StockMovement.objects.select_related("item", "item__condominium", "user")
        movements = _filter_movements_by_user_condominiums(movements, self.request.user)
        if context["selected_condominium"] and _condominium_allowed(self.request.user, context["selected_condominium"]):
            movements = movements.filter(item__condominium_id=context["selected_condominium"])
        if context["selected_sector"]:
            movements = movements.filter(item__sector=context["selected_sector"])
        context["movements"] = movements[:10]
        return context


class StockItemCreateView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, CreateView):
    permissao_required = "cadastrar_produtos"
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"
    success_url = reverse_lazy("estoque:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class StockItemUpdateView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, UpdateView):
    permissao_required = "editar_produtos"
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"

    def get_queryset(self):
        return _filter_by_user_condominiums(super().get_queryset(), self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next") or _item_sector_url(self.object)
        return context

    def get_success_url(self):
        return _safe_next_url(self.request)


class StockItemDeleteView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, DeleteView):
    permissao_required = "excluir_produtos"
    model = StockItem
    template_name = "estoque/item_confirm_delete.html"

    def get_queryset(self):
        return _filter_by_user_condominiums(super().get_queryset(), self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next") or _item_sector_url(self.object)
        return context

    def get_success_url(self):
        return _safe_next_url(self.request)

    def form_valid(self, form):
        messages.success(self.request, "Item excluido com sucesso.")
        return super().form_valid(form)


class StockMovementView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, View):
    permissao_required = "movimentar_estoque"
    movement_type = None
    template_name = "estoque/movement_form.html"

    def get_item(self, pk):
        return get_object_or_404(_filter_by_user_condominiums(StockItem.objects.select_related("condominium"), self.request.user), pk=pk)

    def get(self, request, pk):
        item = self.get_item(pk)
        return self.render_form(request, item, StockMovementForm())

    def post(self, request, pk):
        item = self.get_item(pk)
        form = StockMovementForm(request.POST)
        if form.is_valid():
            try:
                item.move(self.movement_type, form.cleaned_data["quantity"], request.user, form.cleaned_data["notes"])
                messages.success(request, "Movimentacao registrada.")
                return redirect(_safe_next_url(request))
            except ValueError as exc:
                form.add_error("quantity", str(exc))
        return self.render_form(request, item, form)

    def render_form(self, request, item, form):
        from django.shortcuts import render

        next_url = request.GET.get("next") or request.POST.get("next") or _item_sector_url(item)
        return render(request, self.template_name, {"item": item, "form": form, "movement_type": self.movement_type, "next_url": next_url})


class StockEntryView(StockMovementView):
    movement_type = StockMovement.MovementType.ENTRADA


class StockExitView(StockMovementView):
    movement_type = StockMovement.MovementType.SAIDA
