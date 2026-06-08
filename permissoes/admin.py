from django.contrib import admin

from .models import PerfilAcesso, PermissaoModulo, UsuarioPerfil


@admin.register(PermissaoModulo)
class PermissaoModuloAdmin(admin.ModelAdmin):
    list_display = ("nome_modulo", "codigo", "descricao")
    list_filter = ("nome_modulo",)
    search_fields = ("nome_modulo", "codigo", "descricao")
    prepopulated_fields = {"codigo": ("nome_modulo",)}


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao", "total_permissoes")
    search_fields = ("nome", "descricao")
    filter_horizontal = ("permissoes",)

    def total_permissoes(self, obj):
        return obj.permissoes.count()

    total_permissoes.short_description = "permissoes"


@admin.register(UsuarioPerfil)
class UsuarioPerfilAdmin(admin.ModelAdmin):
    list_display = ("usuario", "perfil", "atualizado_em")
    list_filter = ("perfil",)
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name", "perfil__nome")
    autocomplete_fields = ("usuario", "perfil")
