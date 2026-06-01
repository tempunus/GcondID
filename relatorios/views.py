from io import BytesIO

from django.db.models import F
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from chamados.models import Ticket
from estoque.models import StockItem, StockMovement
from users.models import User


def _user_name(user):
    return user.get_full_name() or user.email if user else "-"


def _filter_by_user_condominiums(qs, user):
    if user.is_gcondid_admin:
        return qs
    return qs.filter(condominium__in=user.authorized_condominiums.filter(is_active=True))


def _date_range(request):
    return request.GET.get("start"), request.GET.get("end")


def _rows(kind, request):
    if kind == "estoque":
        qs = _filter_by_user_condominiums(StockItem.objects.select_related("condominium"), request.user)
        sector = request.GET.get("sector")
        if sector:
            qs = qs.filter(sector=sector)
        return ["Condominio", "Nome", "Setor", "Categoria", "Atual", "Minima", "Localizacao"], [
            [i.condominium.name if i.condominium else "-", i.name, i.get_sector_display(), i.category, i.current_quantity, i.minimum_quantity, i.location] for i in qs
        ]
    if kind == "critico":
        qs = _filter_by_user_condominiums(StockItem.objects.select_related("condominium"), request.user).filter(current_quantity__lte=F("minimum_quantity"))
        return ["Condominio", "Nome", "Setor", "Atual", "Minima"], [[i.condominium.name if i.condominium else "-", i.name, i.get_sector_display(), i.current_quantity, i.minimum_quantity] for i in qs]
    if kind == "movimentacoes":
        qs = StockMovement.objects.select_related("item", "item__condominium", "user")
        qs = _filter_by_user_condominiums(qs, request.user)
        start, end = _date_range(request)
        if start:
            qs = qs.filter(created_at__date__gte=start)
        if end:
            qs = qs.filter(created_at__date__lte=end)
        return ["Data", "Condominio", "Item", "Tipo", "Quantidade", "Usuario"], [
            [m.created_at.strftime("%d/%m/%Y %H:%M"), m.item.condominium.name if m.item.condominium else "-", m.item.name, m.get_movement_type_display(), m.quantity, _user_name(m.user)] for m in qs
        ]
    if kind == "chamados":
        qs = _filter_by_user_condominiums(Ticket.objects.select_related("condominium", "requester", "technician"), request.user)
        for field in ("status", "sector", "technician"):
            value = request.GET.get(field)
            if value:
                qs = qs.filter(**{field if field != "technician" else "technician_id": value})
        return ["ID", "Condominio", "Setor", "Status", "Prioridade", "Solicitante", "Tecnico"], [
            [t.id, t.condominium.name if t.condominium else "-", t.get_sector_display(), t.get_status_display(), t.get_priority_display(), _user_name(t.requester), _user_name(t.technician)] for t in qs
        ]
    qs = User.objects.all() if request.user.is_gcondid_admin else User.objects.none()
    return ["Nome", "Email", "Nivel", "Aprovado", "Bloqueado"], [
        [u.get_full_name(), u.email, u.get_access_level_display(), "Sim" if u.is_approved else "Nao", "Sim" if u.is_blocked else "Nao"] for u in qs
    ]


def _staff_allowed(request):
    user = request.user
    if not user.is_authenticated or not user.can_access_panel or not user.has_condominium_access or (not user.is_gcondid_admin and user.access_level != "funcionario"):
        messages.warning(request, "Acesso restrito ou sem condominio autorizado.")
        return False
    return True


@login_required
def reports_index(request):
    if not _staff_allowed(request):
        return redirect("dashboard")
    return render(
        request,
        "relatorios/index.html",
        {"sectors": StockItem.Sector.choices, "ticket_statuses": Ticket.Status.choices, "ticket_sectors": Ticket.Sector.choices, "technicians": User.objects.filter(access_level__in=["admin", "funcionario"]).order_by("first_name", "last_name", "email")},
    )


@login_required
def export_excel(request, kind):
    if not _staff_allowed(request):
        return redirect("dashboard")
    headers, rows = _rows(kind, request)
    wb = Workbook()
    ws = wb.active
    ws.title = kind[:31]
    ws.append(headers)
    for row in rows:
        ws.append(row)
    output = BytesIO()
    wb.save(output)
    response = HttpResponse(output.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="{kind}-{timezone.now():%Y%m%d}.xlsx"'
    return response


@login_required
def export_pdf(request, kind):
    if not _staff_allowed(request):
        return redirect("dashboard")
    headers, rows = _rows(kind, request)
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    width, height = A4
    y = height - 50
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, f"Relatorio GcondID - {kind.title()}")
    y -= 30
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(40, y, " | ".join(headers))
    y -= 18
    pdf.setFont("Helvetica", 8)
    for row in rows:
        pdf.drawString(40, y, " | ".join(str(value)[:22] for value in row))
        y -= 16
        if y < 50:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 8)
    pdf.save()
    response = HttpResponse(output.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{kind}-{timezone.now():%Y%m%d}.pdf"'
    return response


