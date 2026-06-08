from django.core.exceptions import ImproperlyConfigured, PermissionDenied

from .utils import usuario_tem_permissao


class PermissaoRequiredMixin:
    """Mixin para proteger class based views com uma ou mais permissoes do PerfilAcesso."""

    permissao_required = None

    def get_permissao_required(self):
        if not self.permissao_required:
            raise ImproperlyConfigured("Defina permissao_required na view.")
        if isinstance(self.permissao_required, str):
            return [self.permissao_required]
        return list(self.permissao_required)

    def dispatch(self, request, *args, **kwargs):
        permissoes = self.get_permissao_required()
        if not all(usuario_tem_permissao(request.user, codigo) for codigo in permissoes):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
