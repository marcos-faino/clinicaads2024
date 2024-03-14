import base64
from io import BytesIO

from django.views import View
from django.views.generic import TemplateView, ListView
from matplotlib import pyplot

from core.models import Paciente, Consulta, Convenio
from core.util import GeraPDFMixin


class HomeTemplateView(TemplateView):
    template_name = "index.html"


class PacientesListView(ListView):
    template_name = "relatorios/pacientes.html"
    model = Paciente
    context_object_name = 'pacientes'


class RelatPdfPacientes(View, GeraPDFMixin):

    def get(self, request):
        pacientes = Paciente.objects.all()
        data = {
            'pacientes': pacientes,
        }
        return self.gerar_pdf("relatorios/pdfpacientes.html", data)


class ConsConvView(TemplateView):
    template_name = 'graficos/consultasconvenio.html'

    def _criar_grafico(self):
        convenios = Convenio.objects.all()
        glabels = []
        gvalores = []
        for c in convenios:
            if Consulta.objects.filter(convenio=c).count() > 0:
                glabels.append(c.nome)
                quant = Consulta.objects.filter(convenio=c).count()
                gvalores.append(quant)
        pyplot.pie(gvalores, labels=glabels)
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        buffer.seek(0)
        imagem = buffer.getvalue()
        grafico = base64.b64encode(imagem)
        grafico = grafico.decode('utf-8')
        buffer.close()
        return grafico

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        tabela = Consulta.objects.all().order_by('convenio')
        contexto['tabela'] = tabela
        contexto['grafico'] = self._criar_grafico()
        return contexto
