from django.contrib import messages
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, View

from users.mixins import StaffRequiredMixin

from .forms import StockItemForm, StockMovementForm
from .models import StockItem, StockMovement


class StockItemListView(StaffRequiredMixin, ListView):
    model = StockItem
    template_name = "estoque/item_list.html"
    context_object_name = "items"

    def get_queryset(self):
        qs = StockItem.objects.all()
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
        context["movements"] = StockMovement.objects.select_related("item", "user")[:10]
        return context


class StockItemCreateView(StaffRequiredMixin, CreateView):
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"
    success_url = reverse_lazy("estoque:list")


class StockItemUpdateView(StaffRequiredMixin, UpdateView):
    model = StockItem
    form_class = StockItemForm
    template_name = "estoque/item_form.html"
    success_url = reverse_lazy("estoque:list")


class StockMovementView(StaffRequiredMixin, View):
    movement_type = None
    template_name = "estoque/movement_form.html"

    def get(self, request, pk):
        item = get_object_or_404(StockItem, pk=pk)
        return self.render_form(request, item, StockMovementForm())

    def post(self, request, pk):
        item = get_object_or_404(StockItem, pk=pk)
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

# Create your views here.
