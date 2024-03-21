import base64
from io import BytesIO

from django.db.models import Count
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, ListView
from matplotlib import pyplot

from core.models import Paciente, Consulta, Convenio, Possui
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
        pyplot.close()
        buffer.close()
        return grafico

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        tabela = Consulta.objects.all().order_by('convenio')
        contexto['tabela'] = tabela
        contexto['grafico'] = self._criar_grafico()
        return contexto


class GrafPacientesCidade(TemplateView):
    template_name = "graficos/pacporcidade.html"

    def _criar_grafico(self):
        cidades = Paciente.objects.distinct().values_list('cidade',flat=True)
        pacientes = Paciente.objects.all()
        glabels = []
        gvalores = []
        for c in cidades:
            glabels.append(c)
            quant = pacientes.filter(cidade=c).count()
            gvalores.append(quant)
        pyplot.bar(glabels, gvalores)
        buffer = BytesIO()
        pyplot.savefig(buffer, format='png')
        buffer.seek(0)
        img = buffer.getvalue()
        graf = base64.b64encode(img)
        graf = graf.decode('utf-8')
        pyplot.close()
        buffer.close()
        return graf

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['grafico'] = self._criar_grafico()
        return contexto



class PacientePorConvenioListView(ListView):
    template_name = 'graficos/pacconvgooglechart.html'
    model = Paciente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        convenios = Convenio.objects.all()
        dados=[]
        for c in convenios:
            dados.append(
                {
                    'convenio': c.nome,
                    'pacientes': Possui.objects.filter(convenio=c.codconv).count()
                }
            )
        contexto['dados'] = dados
        return contexto


class RelatorioConsultasAno(View):

    def get(self, request, ano):
        meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
        data = []
        labels = []
        # consultas = Consulta.objects.all().values('data__year').annotate(total=Count(id))
        consultasano = Consulta.objects.all().filter(data__year=ano)
        consultas = consultasano.values('data__month').annotate(total=Count(id))
        for i in range(1, 12):
            labels.append(meses[i-1])
            for c in consultas:
                if i == c['data__month']:
                    data.append(c['total'])
            data.append(0)

        return JsonResponse({'labels':labels, 'data': data})


class EscolhaMesView(TemplateView):
    template_name = "graficos/dashboardchartjs.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        anos = Consulta.objects.all().values('data__year').distinct()
        ctx['anos'] = anos
        return ctx