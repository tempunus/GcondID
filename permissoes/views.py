from django.views.generic import CreateView, TemplateView

from .decorators import tem_permissao
from .mixins import PermissaoRequiredMixin


@tem_permissao("visualizar_relatorios")
def exemplo_relatorio_view(request):
    """Exemplo de function based view protegida por decorator."""
    from django.http import HttpResponse

    return HttpResponse("Relatorio protegido por permissao.")


class ExemploProdutoCreateView(PermissaoRequiredMixin, CreateView):
    """Exemplo de class based view protegida por permissao."""

    permissao_required = "cadastrar_produtos"
    fields = []
    template_name = "permissoes/exemplo_template.html"


class ExemploTemplateView(TemplateView):
    template_name = "permissoes/exemplo_template.html"
