from django.conf import settings
from django.db import models


class PermissaoModulo(models.Model):
    """Permissao atomica usada para liberar uma acao ou tela do sistema."""

    nome_modulo = models.CharField("modulo", max_length=100)
    codigo = models.SlugField("codigo", max_length=100, unique=True)
    descricao = models.TextField("descricao", blank=True)

    class Meta:
        ordering = ["nome_modulo", "codigo"]
        verbose_name = "permissao de modulo"
        verbose_name_plural = "permissoes de modulo"

    def __str__(self):
        return f"{self.nome_modulo} - {self.codigo}"


class PerfilAcesso(models.Model):
    """Agrupa permissoes para que o administrador aplique a um usuario."""

    nome = models.CharField("nome", max_length=100, unique=True)
    descricao = models.TextField("descricao", blank=True)
    permissoes = models.ManyToManyField(PermissaoModulo, blank=True, related_name="perfis", verbose_name="permissoes")

    class Meta:
        ordering = ["nome"]
        verbose_name = "perfil de acesso"
        verbose_name_plural = "perfis de acesso"

    def __str__(self):
        return self.nome


class UsuarioPerfil(models.Model):
    """Vincula cada usuario a exatamente um perfil de acesso."""

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfil_acesso", verbose_name="usuario")
    perfil = models.ForeignKey(PerfilAcesso, on_delete=models.PROTECT, related_name="usuarios", verbose_name="perfil")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["usuario__email"]
        verbose_name = "perfil do usuario"
        verbose_name_plural = "perfis dos usuarios"

    def __str__(self):
        return f"{self.usuario} - {self.perfil}"
