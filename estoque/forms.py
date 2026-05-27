from django import forms

from .models import StockItem


class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ("name", "category", "sector", "current_quantity", "minimum_quantity", "location")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "name": "Nome do item",
            "category": "Categoria",
            "current_quantity": "Quantidade atual",
            "minimum_quantity": "Quantidade minima",
            "location": "Localizacao do item",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({"placeholder": placeholders.get(name, field.label)})


class StockMovementForm(forms.Form):
    quantity = forms.IntegerField(label="Quantidade", min_value=1)
    notes = forms.CharField(label="Observacoes", widget=forms.Textarea(attrs={"rows": 3}), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["quantity"].widget.attrs.update({"placeholder": "Quantidade movimentada"})
        self.fields["notes"].widget.attrs.update({"placeholder": "Detalhes da movimentacao"})
