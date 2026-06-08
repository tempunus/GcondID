def usuario_tem_permissao(user, codigo):
    """Retorna True quando o usuario possui a permissao via perfil.

    Superusuarios e usuarios com perfil legado Administrador continuam tendo acesso total.
    Isso evita bloquear o administrador durante a configuracao inicial dos perfis.
    """

    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False) or getattr(user, "is_gcondid_admin", False):
        return True
    perfil_usuario = getattr(user, "perfil_acesso", None)
    if not perfil_usuario:
        return False
    return perfil_usuario.perfil.permissoes.filter(codigo=codigo).exists()
