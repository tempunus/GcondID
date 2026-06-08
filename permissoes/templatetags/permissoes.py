from django import template

from permissoes.utils import usuario_tem_permissao

register = template.Library()


@register.filter
def possui_permissao(user, codigo):
    """Uso no template: {% if user|possui_permissao:'cadastrar_produtos' %}."""

    return usuario_tem_permissao(user, codigo)
