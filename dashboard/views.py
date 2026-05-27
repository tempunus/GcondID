from django.db.models import Count, F
from django.views.generic import TemplateView

from chamados.models import Ticket
from estoque.models import StockItem, StockMovement
from users.mixins import ApprovedUserRequiredMixin
from users.models import User


class DashboardView(ApprovedUserRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ticket_counts = dict(Ticket.objects.values_list("status").annotate(total=Count("id")))
        context.update(
            {
                "total_users": User.objects.count(),
                "tickets_open": ticket_counts.get(Ticket.Status.ABERTO, 0),
                "tickets_progress": ticket_counts.get(Ticket.Status.EM_ANDAMENTO, 0),
                "tickets_done": ticket_counts.get(Ticket.Status.CONCLUIDO, 0),
                "critical_stock": StockItem.objects.filter(current_quantity__lte=F("minimum_quantity")).count(),
                "recent_movements": StockMovement.objects.select_related("item", "user")[:6],
            }
        )
        return context

# Create your views here.
