from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "auth-input", "placeholder": "Email"})
        self.fields["password"].widget.attrs.update({"class": "auth-input", "placeholder": "Senha"})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.can_access_panel:
            raise forms.ValidationError(
                "Sua conta esta pendente, bloqueada ou inativa. Aguarde a aprovacao do administrador.",
                code="inactive",
            )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        placeholders = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "Email",
            "phone": "WhatsApp com DDD",
            "password1": "Senha",
            "password2": "Confirmar senha",
        }
        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "auth-input", "placeholder": placeholders.get(name, field.label)})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.is_approved = False
        user.access_level = User.AccessLevel.VISITANTE
        if commit:
            user.save()
        return user


class AdminUserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "access_level",
            "is_approved",
            "is_blocked",
            "is_active",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["is_approved"].initial = True
        self.fields["is_active"].initial = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
        return user


class UserApprovalForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "access_level", "is_approved", "is_blocked", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
