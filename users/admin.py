from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from permissoes.models import UsuarioPerfil

from .models import User


class UsuarioPerfilInline(admin.StackedInline):
    model = UsuarioPerfil
    extra = 0
    max_num = 1
    can_delete = False
    autocomplete_fields = ("perfil",)


@admin.register(User)
class GcondIDUserAdmin(UserAdmin):
    list_display = ("email", "first_name", "perfil_nome", "access_level", "is_approved", "is_blocked", "is_staff")
    list_filter = ("access_level", "perfil_acesso__perfil", "is_approved", "is_blocked", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("authorized_condominiums",)
    inlines = (UsuarioPerfilInline,)
    fieldsets = UserAdmin.fieldsets + (
        ("GcondID", {"fields": ("access_level", "authorized_condominiums", "is_approved", "is_blocked")}),
    )

    def perfil_nome(self, obj):
        perfil_usuario = getattr(obj, "perfil_acesso", None)
        return perfil_usuario.perfil.nome if perfil_usuario else "Sem perfil"

    perfil_nome.short_description = "perfil de acesso"
