from django import forms

from .models import Condominium


class CondominiumForm(forms.ModelForm):
    class Meta:
        model = Condominium
        fields = ("name", "cnpj", "address", "city", "state", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "name": "Nome do condominio",
            "cnpj": "CNPJ",
            "address": "Endereco completo",
            "city": "Cidade",
            "state": "UF",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": placeholders.get(name, field.label)})
