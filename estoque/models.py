from django.conf import settings
from django.db import models
from django.utils import timezone


class StockItem(models.Model):
    class Sector(models.TextChoices):
        ESCRITORIO = "escritorio", "Escritorio"
        LIMPEZA = "limpeza", "Limpeza"
        MANUTENCAO = "manutencao", "Manutencao"

    name = models.CharField("nome", max_length=150)
    category = models.CharField("categoria", max_length=120)
    sector = models.CharField("setor", max_length=30, choices=Sector.choices)
    current_quantity = models.PositiveIntegerField("quantidade atual", default=0)
    minimum_quantity = models.PositiveIntegerField("quantidade minima", default=0)
    location = models.CharField("localizacao", max_length=150, blank=True)
    last_entry_at = models.DateTimeField("ultima entrada", null=True, blank=True)
    last_exit_at = models.DateTimeField("ultima saida", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sector", "name"]

    def __str__(self):
        return self.name

    @property
    def is_critical(self):
        return self.current_quantity <= self.minimum_quantity

    def move(self, movement_type, quantity, user=None, notes=""):
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if movement_type == StockMovement.MovementType.SAIDA and quantity > self.current_quantity:
            raise ValueError("Quantidade insuficiente em estoque.")
        if movement_type == StockMovement.MovementType.ENTRADA:
            self.current_quantity += quantity
            self.last_entry_at = timezone.now()
        else:
            self.current_quantity -= quantity
            self.last_exit_at = timezone.now()
        self.save()
        return StockMovement.objects.create(item=self, movement_type=movement_type, quantity=quantity, user=user, notes=notes)


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saida"

    item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField("tipo", max_length=20, choices=MovementType.choices)
    quantity = models.PositiveIntegerField("quantidade")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField("observacoes", blank=True)
    created_at = models.DateTimeField("data", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.item} ({self.quantity})"

# Create your models here.
