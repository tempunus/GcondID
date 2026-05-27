from django.conf import settings
from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    class Sector(models.TextChoices):
        ESCRITORIO = "escritorio", "Escritorio"
        LIMPEZA = "limpeza", "Limpeza"
        MANUTENCAO = "manutencao", "Manutencao"
        AREA_EXTERNA = "area_externa", "Area externa"
        OUTROS = "outros", "Outros"

    class Priority(models.TextChoices):
        BAIXA = "baixa", "Baixa"
        MEDIA = "media", "Media"
        ALTA = "alta", "Alta"
        URGENTE = "urgente", "Urgente"

    class Status(models.TextChoices):
        ABERTO = "aberto", "Aberto"
        EM_ANDAMENTO = "em_andamento", "Em andamento"
        AGUARDANDO_PECA = "aguardando_peca", "Aguardando peca"
        CONCLUIDO = "concluido", "Concluido"

    sector = models.CharField("setor", max_length=30, choices=Sector.choices)
    description = models.TextField("descricao do problema")
    priority = models.CharField("prioridade", max_length=20, choices=Priority.choices, default=Priority.MEDIA)
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="requested_tickets")
    technician = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_tickets")
    status = models.CharField("status", max_length=30, choices=Status.choices, default=Status.ABERTO)
    opening_photo = models.ImageField("foto de abertura", upload_to="chamados/abertura/", blank=True)
    completion_photo = models.ImageField("foto de conclusao", upload_to="chamados/conclusao/", blank=True)
    solution = models.TextField("solucao aplicada", blank=True)
    completed_at = models.DateTimeField("data de conclusao", null=True, blank=True)
    created_at = models.DateTimeField("aberto em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Chamado #{self.pk} - {self.get_sector_display()}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.CONCLUIDO and self.completed_at is None:
            self.completed_at = timezone.now()
        if self.status != self.Status.CONCLUIDO:
            self.completed_at = None
        super().save(*args, **kwargs)


class TicketNotification(models.Model):
    class Channel(models.TextChoices):
        EMAIL = "email", "Email"
        WHATSAPP = "whatsapp", "WhatsApp"

    class Status(models.TextChoices):
        SENT = "sent", "Enviado"
        FAILED = "failed", "Falhou"
        SKIPPED = "skipped", "Nao configurado"

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    channel = models.CharField("canal", max_length=20, choices=Channel.choices)
    status = models.CharField("status", max_length=20, choices=Status.choices)
    message = models.TextField("mensagem", blank=True)
    response = models.TextField("resposta", blank=True)
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
