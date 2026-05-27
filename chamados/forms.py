from django import forms

from users.models import User

from .models import Ticket


class ResponsibleUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.get_full_name() or obj.email


class TicketCreateForm(forms.ModelForm):
    technician = ResponsibleUserChoiceField(queryset=User.objects.none(), label="Usuario responsavel")

    class Meta:
        model = Ticket
        fields = ("sector", "description", "priority", "technician", "opening_photo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].label = "Usuario responsavel"
        self.fields["technician"].required = True
        self.fields["technician"].queryset = User.objects.filter(
            is_approved=True,
            is_blocked=False,
            is_active=True,
            access_level__in=[User.AccessLevel.ADMIN, User.AccessLevel.FUNCIONARIO],
        ).order_by("first_name", "last_name", "email")
        self.fields["description"].widget.attrs.update({"placeholder": "Descreva o problema com detalhes", "rows": 4})


class TicketUpdateForm(forms.ModelForm):
    technician = ResponsibleUserChoiceField(queryset=User.objects.none(), label="Usuario responsavel")

    class Meta:
        model = Ticket
        fields = ("sector", "description", "priority", "technician", "status", "opening_photo", "completion_photo", "solution")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["technician"].label = "Usuario responsavel"
        self.fields["technician"].queryset = User.objects.filter(
            is_approved=True,
            is_blocked=False,
            is_active=True,
            access_level__in=[User.AccessLevel.ADMIN, User.AccessLevel.FUNCIONARIO],
        ).order_by("first_name", "last_name", "email")
        self.fields["description"].widget.attrs.update({"placeholder": "Descreva o problema com detalhes", "rows": 4})
        self.fields["solution"].widget.attrs.update({"placeholder": "Informe a solucao aplicada", "rows": 4})
