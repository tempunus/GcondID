from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from permissoes.models import PerfilAcesso, UsuarioPerfil

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
        if not user.has_condominium_access:
            raise forms.ValidationError(
                "Voce nao tem acesso autorizado a nenhum condominio. Solicite liberacao ao administrador.",
                code="no_condominium_access",
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


class PerfilUsuarioFormMixin:
    perfil = forms.ModelChoiceField(
        label="Perfil de acesso",
        queryset=PerfilAcesso.objects.all(),
        required=True,
        help_text="Define exatamente quais telas e funcionalidades o usuario podera acessar.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["perfil"].queryset = PerfilAcesso.objects.order_by("nome")
        perfil_usuario = getattr(self.instance, "perfil_acesso", None) if getattr(self, "instance", None) else None
        if perfil_usuario:
            self.fields["perfil"].initial = perfil_usuario.perfil

    def save_usuario_perfil(self, user):
        perfil = self.cleaned_data.get("perfil")
        if perfil:
            UsuarioPerfil.objects.update_or_create(usuario=user, defaults={"perfil": perfil})


class AdminUserCreateForm(PerfilUsuarioFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "access_level",
            "authorized_condominiums",
            "is_approved",
            "is_blocked",
            "is_active",
            "password1",
            "password2",
        )
        widgets = {"authorized_condominiums": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["is_approved"].initial = True
        self.fields["is_active"].initial = True
        self.fields["authorized_condominiums"].label = "Condominios autorizados"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        if commit:
            user.save()
            self.save_m2m()
            self.save_usuario_perfil(user)
        return user


class UserApprovalForm(PerfilUsuarioFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "access_level", "authorized_condominiums", "is_approved", "is_blocked", "is_active")
        widgets = {"authorized_condominiums": forms.CheckboxSelectMultiple}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["authorized_condominiums"].label = "Condominios autorizados"

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            self.save_usuario_perfil(user)
        return user
