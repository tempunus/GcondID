from django.db.models import Count, F
from django.views.generic import TemplateView

from chamados.models import Ticket
from estoque.models import StockItem, StockMovement
from users.mixins import ApprovedUserRequiredMixin
from users.models import User


def _filter_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(condominium__in=user.authorized_condominiums.filter(is_active=True))


class DashboardView(ApprovedUserRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tickets = _filter_by_user_condominiums(Ticket.objects.all(), self.request.user)
        stock_items = _filter_by_user_condominiums(StockItem.objects.all(), self.request.user)
        movements = StockMovement.objects.select_related("item", "item__condominium", "user")
        movements = _filter_movements_by_user_condominiums(movements, self.request.user)
        ticket_counts = dict(tickets.values_list("status").annotate(total=Count("id")))
        context.update(
            {
                "total_users": User.objects.count(),
                "tickets_open": ticket_counts.get(Ticket.Status.ABERTO, 0),
                "tickets_progress": ticket_counts.get(Ticket.Status.EM_ANDAMENTO, 0),
                "tickets_done": ticket_counts.get(Ticket.Status.CONCLUIDO, 0),
                "critical_stock": stock_items.filter(current_quantity__lte=F("minimum_quantity")).count(),
                "recent_movements": movements[:6],
            }
        )
        return context

