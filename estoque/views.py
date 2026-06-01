from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from users.mixins import StaffRequiredMixin

from .forms import StockItemForm, StockMovementForm
from .models import StockItem, StockMovement


def _filter_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(condominium__in=user.authorized_condominiums.filter(is_active=True))


def _filter_movements_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(item__condominium__in=user.authorized_condominiums.filter(is_active=True))


class StockItemListView(StaffRequiredMixin, ListView):
    model = StockItem
    template_name = "estoque/item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        qs = _filter_by_user_condominiums(StockItem.objects.select_related("condominium"), self.request.user)
        sector = self.request.GET.get("sector")
        critical = self.request.GET.get("critical")
        if sector:
            qs = qs.filter(sector=sector)
        if critical:
            qs = qs.filter(current_quantity__lte=F("minimum_quantity"))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sectors"] = StockItem.Sector.choices
        movements = StockMovement.objects.select_related("item", "item__condominium", "user")
        context["movements"] = _filter_movements_by_user_condominiums(movements, self.request.user)[:10]
        return context


class StockItemCreateView(StaffRequiredMixin, CreateView):
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"
    success_url = reverse_lazy("estoque:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class StockItemUpdateView(StaffRequiredMixin, UpdateView):
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"
    success_url = reverse_lazy("estoque:list")

    def get_queryset(self):
        return _filter_by_user_condominiums(super().get_queryset(), self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs


class StockMovementView(StaffRequiredMixin, View):
    movement_type = None
    template_name = "estoque/movement_form.html"

    def get_item(self, pk):
        return get_object_or_404(_filter_by_user_condominiums(StockItem.objects.all(), self.request.user), pk=pk)

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
                return redirect("estoque:list")
            except ValueError as exc:
                form.add_error("quantity", str(exc))
        return self.render_form(request, item, form)

    def render_form(self, request, item, form):
        from django.shortcuts import render

        return render(request, self.template_name, {"item": item, "form": form, "movement_type": self.movement_type})


class StockEntryView(StockMovementView):
    movement_type = StockMovement.MovementType.ENTRADA


class StockExitView(StockMovementView):
    movement_type = StockMovement.MovementType.SAIDA
