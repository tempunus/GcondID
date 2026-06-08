from functools import wraps

from django.core.exceptions import PermissionDenied

from .utils import usuario_tem_permissao


def tem_permissao(codigo):
    """Bloqueia uma function based view quando o usuario nao possui a permissao."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not usuario_tem_permissao(request.user, codigo):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
