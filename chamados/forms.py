from django import forms
from django.db.models import Q

from users.models import User

from .models import Ticket


class ResponsibleUserChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.display_name


def _responsible_users_queryset():
    return (
        User.objects.filter(
            is_approved=True,
            is_blocked=False,
            is_active=True,
            access_level__in=[User.AccessLevel.ADMIN, User.AccessLevel.FUNCIONARIO],
        )
        .filter(Q(access_level=User.AccessLevel.ADMIN) | Q(is_superuser=True) | Q(authorized_condominiums__is_active=True))
        .distinct()
        .order_by("first_name", "last_name", "email")
    )


class TicketCreateForm(forms.ModelForm):
    technician = ResponsibleUserChoiceField(queryset=User.objects.none(), label="Usuario responsavel")

    class Meta:
        model = Ticket
        fields = ("condominium", "sector", "description", "priority", "technician", "opening_photo")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_gcondid_admin:
            self.fields["condominium"].queryset = self.user.authorized_condominiums.filter(is_active=True)
        else:
            self.fields["condominium"].queryset = self.fields["condominium"].queryset.filter(is_active=True)
        self.fields["condominium"].required = True
        self.fields["technician"].label = "Usuario responsavel"
        self.fields["technician"].required = True
        self.fields["technician"].queryset = _responsible_users_queryset()
        self.fields["description"].widget.attrs.update({"placeholder": "Descreva o problema com detalhes", "rows": 4})

    def clean(self):
        cleaned_data = super().clean()
        condominium = cleaned_data.get("condominium")
        technician = cleaned_data.get("technician")
        if condominium and technician and not technician.is_gcondid_admin:
            allowed = technician.authorized_condominiums.filter(pk=condominium.pk, is_active=True).exists()
            if not allowed:
                self.add_error("technician", "O responsavel selecionado nao tem autorizacao para este condominio.")
        return cleaned_data


class TicketUpdateForm(forms.ModelForm):
    technician = ResponsibleUserChoiceField(queryset=User.objects.none(), label="Usuario responsavel")

    class Meta:
        model = Ticket
        fields = ("condominium", "sector", "description", "priority", "technician", "status", "opening_photo", "completion_photo", "solution")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_gcondid_admin:
            self.fields["condominium"].queryset = self.user.authorized_condominiums.filter(is_active=True)
        else:
            self.fields["condominium"].queryset = self.fields["condominium"].queryset.filter(is_active=True)
        self.fields["condominium"].required = True
        self.fields["technician"].label = "Usuario responsavel"
        self.fields["technician"].queryset = _responsible_users_queryset()
        self.fields["description"].widget.attrs.update({"placeholder": "Descreva o problema com detalhes", "rows": 4})
        self.fields["solution"].widget.attrs.update({"placeholder": "Informe a solucao aplicada", "rows": 4})

    def clean(self):
        cleaned_data = super().clean()
        condominium = cleaned_data.get("condominium")
        technician = cleaned_data.get("technician")
        if condominium and technician and not technician.is_gcondid_admin:
            allowed = technician.authorized_condominiums.filter(pk=condominium.pk, is_active=True).exists()
            if not allowed:
                self.add_error("technician", "O responsavel selecionado nao tem autorizacao para este condominio.")
        return cleaned_data
