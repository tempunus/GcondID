# Generated manually for the GcondID permission system.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


PERMISSOES = [
    ("Estoque", "acessar_estoque", "Permite acessar o modulo de estoque."),
    ("Estoque", "cadastrar_produtos", "Permite cadastrar itens/produtos no estoque."),
    ("Estoque", "editar_produtos", "Permite editar itens/produtos do estoque."),
    ("Estoque", "excluir_produtos", "Permite excluir itens/produtos do estoque."),
    ("Estoque", "movimentar_estoque", "Permite registrar entrada ou baixa no estoque."),
    ("Chamados", "abrir_chamados", "Permite abrir chamados."),
    ("Chamados", "concluir_chamados", "Permite concluir chamados."),
    ("Chamados", "visualizar_chamados", "Permite visualizar chamados."),
    ("Chamados", "editar_chamados", "Permite editar chamados."),
    ("Usuarios", "cadastrar_usuarios", "Permite cadastrar usuarios."),
    ("Usuarios", "editar_usuarios", "Permite editar usuarios."),
    ("Usuarios", "excluir_usuarios", "Permite excluir usuarios."),
    ("Usuarios", "visualizar_usuarios", "Permite visualizar usuarios."),
    ("Relatorios", "visualizar_relatorios", "Permite visualizar e exportar relatorios."),
    ("Condominios", "administrar_condominio", "Permite administrar cadastros de condominios."),
]

PERFIS = {
    "Administrador": [codigo for _, codigo, _ in PERMISSOES],
    "Sindico": [
        "visualizar_chamados",
        "abrir_chamados",
        "editar_chamados",
        "concluir_chamados",
        "acessar_estoque",
        "visualizar_relatorios",
    ],
    "Porteiro": ["visualizar_chamados", "abrir_chamados"],
    "Zelador": ["visualizar_chamados", "abrir_chamados", "editar_chamados", "concluir_chamados"],
    "Morador": ["visualizar_chamados", "abrir_chamados"],
    "Almoxarifado": ["acessar_estoque", "cadastrar_produtos", "editar_produtos", "excluir_produtos", "movimentar_estoque"],
    "Financeiro": ["visualizar_relatorios"],
}


def criar_dados_iniciais(apps, schema_editor):
    PermissaoModulo = apps.get_model("permissoes", "PermissaoModulo")
    PerfilAcesso = apps.get_model("permissoes", "PerfilAcesso")
    permissoes_por_codigo = {}
    for nome_modulo, codigo, descricao in PERMISSOES:
        permissao, _ = PermissaoModulo.objects.update_or_create(
            codigo=codigo,
            defaults={"nome_modulo": nome_modulo, "descricao": descricao},
        )
        permissoes_por_codigo[codigo] = permissao
    for nome, codigos in PERFIS.items():
        perfil, _ = PerfilAcesso.objects.update_or_create(
            nome=nome,
            defaults={"descricao": f"Perfil padrao: {nome}."},
        )
        perfil.permissoes.set([permissoes_por_codigo[codigo] for codigo in codigos])

    User = apps.get_model("users", "User")
    UsuarioPerfil = apps.get_model("permissoes", "UsuarioPerfil")
    perfil_admin = PerfilAcesso.objects.get(nome="Administrador")
    perfil_funcionario = PerfilAcesso.objects.get(nome="Zelador")
    perfil_visitante = PerfilAcesso.objects.get(nome="Morador")
    for usuario in User.objects.all():
        if usuario.is_superuser or getattr(usuario, "access_level", "") == "admin":
            perfil = perfil_admin
        elif getattr(usuario, "access_level", "") == "funcionario":
            perfil = perfil_funcionario
        else:
            perfil = perfil_visitante
        UsuarioPerfil.objects.get_or_create(usuario=usuario, defaults={"perfil": perfil})


def remover_dados_iniciais(apps, schema_editor):
    PerfilAcesso = apps.get_model("permissoes", "PerfilAcesso")
    PermissaoModulo = apps.get_model("permissoes", "PermissaoModulo")
    PerfilAcesso.objects.filter(nome__in=PERFIS.keys()).delete()
    PermissaoModulo.objects.filter(codigo__in=[codigo for _, codigo, _ in PERMISSOES]).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PermissaoModulo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome_modulo", models.CharField(max_length=100, verbose_name="modulo")),
                ("codigo", models.SlugField(max_length=100, unique=True, verbose_name="codigo")),
                ("descricao", models.TextField(blank=True, verbose_name="descricao")),
            ],
            options={
                "verbose_name": "permissao de modulo",
                "verbose_name_plural": "permissoes de modulo",
                "ordering": ["nome_modulo", "codigo"],
            },
        ),
        migrations.CreateModel(
            name="PerfilAcesso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, unique=True, verbose_name="nome")),
                ("descricao", models.TextField(blank=True, verbose_name="descricao")),
                ("permissoes", models.ManyToManyField(blank=True, related_name="perfis", to="permissoes.permissaomodulo", verbose_name="permissoes")),
            ],
            options={
                "verbose_name": "perfil de acesso",
                "verbose_name_plural": "perfis de acesso",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="UsuarioPerfil",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("perfil", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="usuarios", to="permissoes.perfilacesso", verbose_name="perfil")),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="perfil_acesso", to=settings.AUTH_USER_MODEL, verbose_name="usuario")),
            ],
            options={
                "verbose_name": "perfil do usuario",
                "verbose_name_plural": "perfis dos usuarios",
                "ordering": ["usuario__email"],
            },
        ),
        migrations.RunPython(criar_dados_iniciais, remover_dados_iniciais),
    ]


