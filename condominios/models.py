from django.db import models


class Condominium(models.Model):
    name = models.CharField("nome", max_length=160)
    cnpj = models.CharField("CNPJ", max_length=20, blank=True)
    address = models.CharField("endereco", max_length=220, blank=True)
    city = models.CharField("cidade", max_length=100, blank=True)
    state = models.CharField("UF", max_length=2, blank=True)
    is_active = models.BooleanField("ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "condominio"
        verbose_name_plural = "condominios"

    def __str__(self):
        return self.name
