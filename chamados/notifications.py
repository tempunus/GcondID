import json
from urllib import request
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.core.mail import send_mail

from .models import TicketNotification


def _ticket_message(ticket):
    responsible = getattr(ticket.technician, "display_name", None) or ticket.technician.get_full_name() or f"Usuario #{ticket.technician_id}"
    return (
        f"Ola, {responsible}.\n\n"
        f"Um chamado foi direcionado para voce no GcondID.\n"
        f"Chamado: #{ticket.pk}\n"
        f"Setor: {ticket.get_sector_display()}\n"
        f"Prioridade: {ticket.get_priority_display()}\n"
        f"Status: {ticket.get_status_display()}\n\n"
        f"Descricao:\n{ticket.description}"
    )


def notify_ticket_assignee(ticket):
    if not ticket.technician:
        return
    message = _ticket_message(ticket)
    _send_email(ticket, message)
    _send_whatsapp(ticket, message)


def _send_email(ticket, message):
    try:
        sent = send_mail(
            subject=f"GcondID - Chamado #{ticket.pk} direcionado a voce",
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "gcondid@localhost"),
            recipient_list=[ticket.technician.email],
            fail_silently=False,
        )
        status = TicketNotification.Status.SENT if sent else TicketNotification.Status.FAILED
        response = "Email enviado pelo backend configurado." if sent else "Nenhum email enviado."
    except Exception as exc:
        status = TicketNotification.Status.FAILED
        response = str(exc)
    TicketNotification.objects.create(
        ticket=ticket,
        recipient=ticket.technician,
        channel=TicketNotification.Channel.EMAIL,
        status=status,
        message=message,
        response=response,
    )


def _send_whatsapp(ticket, message):
    phone = _normalize_whatsapp_phone(ticket.technician.phone)
    if not phone:
        _log_whatsapp(ticket, TicketNotification.Status.SKIPPED, message, "Usuario sem telefone/WhatsApp cadastrado.")
        return

    provider = getattr(settings, "WHATSAPP_PROVIDER", "webhook").lower()
    if provider == "meta":
        _send_whatsapp_meta(ticket, phone, message)
        return

    _send_whatsapp_webhook(ticket, phone, message)


def _normalize_whatsapp_phone(phone):
    digits = "".join(char for char in phone if char.isdigit())
    if len(digits) in {10, 11}:
        return f"55{digits}"
    return digits


def _send_whatsapp_webhook(ticket, phone, message):
    webhook_url = getattr(settings, "WHATSAPP_WEBHOOK_URL", "")
    if not webhook_url:
        _log_whatsapp(
            ticket,
            TicketNotification.Status.SKIPPED,
            message,
            f"Configure WHATSAPP_WEBHOOK_URL ou use WHATSAPP_PROVIDER=meta. Destino: {phone}",
        )
        return
    payload = json.dumps({"phone": phone, "message": message, "ticket_id": ticket.pk}).encode("utf-8")
    req = request.Request(webhook_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8", errors="replace")
        status = TicketNotification.Status.SENT
        response_text = body or "WhatsApp enviado pelo webhook configurado."
    except (URLError, TimeoutError, Exception) as exc:
        status = TicketNotification.Status.FAILED
        response_text = str(exc)
    _log_whatsapp(ticket, status, message, response_text)


def _send_whatsapp_meta(ticket, phone, message):
    phone_number_id = getattr(settings, "WHATSAPP_META_PHONE_NUMBER_ID", "")
    access_token = getattr(settings, "WHATSAPP_META_ACCESS_TOKEN", "")
    api_version = getattr(settings, "WHATSAPP_META_API_VERSION", "v25.0")
    if not phone_number_id or not access_token:
        _log_whatsapp(
            ticket,
            TicketNotification.Status.SKIPPED,
            message,
            "Configure WHATSAPP_META_PHONE_NUMBER_ID e WHATSAPP_META_ACCESS_TOKEN.",
        )
        return

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "text",
            "text": {"preview_url": False, "body": message},
        }
    ).encode("utf-8")
    req = request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=10) as response:
            response_text = response.read().decode("utf-8", errors="replace")
        status = TicketNotification.Status.SENT
    except HTTPError as exc:
        status = TicketNotification.Status.FAILED
        response_text = exc.read().decode("utf-8", errors="replace") or str(exc)
    except (URLError, TimeoutError, Exception) as exc:
        status = TicketNotification.Status.FAILED
        response_text = str(exc)
    _log_whatsapp(ticket, status, message, response_text)


def _log_whatsapp(ticket, status, message, response):
    TicketNotification.objects.create(
        ticket=ticket,
        recipient=ticket.technician,
        channel=TicketNotification.Channel.WHATSAPP,
        status=status,
        message=message,
        response=response,
    )
