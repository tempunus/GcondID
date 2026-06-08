from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from condominios.models import Condominium
from permissoes.mixins import PermissaoRequiredMixin
from permissoes.utils import usuario_tem_permissao
from users.mixins import ApprovedUserRequiredMixin

from .forms import TicketCreateForm, TicketUpdateForm
from .models import Ticket
from .notifications import notify_ticket_assignee


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


class TicketListView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, ListView):
    permissao_required = "visualizar_chamados"
    model = Ticket
    template_name = "chamados/ticket_list.html"
    context_object_name = "tickets"

    def get_queryset(self):
        qs = _filter_by_user_condominiums(Ticket.objects.select_related("condominium", "requester", "technician"), self.request.user)
        user = self.request.user
        if not user.is_gcondid_admin and user.access_level == "visitante":
            qs = qs.filter(requester=user)
        status = self.request.GET.get("status")
        sector = self.request.GET.get("sector")
        condominium = self.request.GET.get("condominium")
        technician = self.request.GET.get("technician")
        if condominium:
            if not _condominium_allowed(user, condominium):
                messages.warning(self.request, "Voce nao tem autorizacao para acessar este condominio.")
                return qs.none()
            qs = qs.filter(condominium_id=condominium)
        if status:
            qs = qs.filter(status=status)
        if sector:
            qs = qs.filter(sector=sector)
        if technician:
            qs = qs.filter(technician_id=technician)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Ticket.Status.choices
        context["sectors"] = Ticket.Sector.choices
        context["condominiums"] = _authorized_condominiums(self.request.user)
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_sector"] = self.request.GET.get("sector", "")
        context["selected_condominium"] = self.request.GET.get("condominium", "")
        return context


class TicketCreateView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, CreateView):
    permissao_required = "abrir_chamados"
    model = Ticket
    form_class = TicketCreateForm
    template_name = "chamados/ticket_form.html"
    success_url = reverse_lazy("chamados:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.requester = self.request.user
        response = super().form_valid(form)
        notify_ticket_assignee(self.object)
        messages.success(self.request, "Chamado aberto e notificacao enviada ao responsavel.")
        return response


class TicketUpdateView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, UpdateView):
    permissao_required = "editar_chamados"
    model = Ticket
    form_class = TicketUpdateForm
    template_name = "chamados/ticket_form.html"
    success_url = reverse_lazy("chamados:list")

    def get_queryset(self):
        return _filter_by_user_condominiums(super().get_queryset(), self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        old_technician_id = self.get_object().technician_id
        response = super().form_valid(form)
        if self.object.technician_id and self.object.technician_id != old_technician_id:
            notify_ticket_assignee(self.object)
            messages.success(self.request, "Chamado atualizado e novo responsavel notificado.")
        else:
            messages.success(self.request, "Chamado atualizado.")
        return response


class TicketDetailView(PermissaoRequiredMixin, ApprovedUserRequiredMixin, DetailView):
    permissao_required = "visualizar_chamados"
    model = Ticket
    template_name = "chamados/ticket_detail.html"
    context_object_name = "ticket"

    def get_queryset(self):
        qs = _filter_by_user_condominiums(super().get_queryset(), self.request.user)
        if not self.request.user.is_gcondid_admin and self.request.user.access_level == "visitante":
            qs = qs.filter(requester=self.request.user)
        return qs
