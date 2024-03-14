from django.urls import path

from core import views

urlpatterns = [
    path('', views.HomeTemplateView.as_view(), name='home'),
    path('relatorios/pacientes', views.PacientesListView.as_view(),
         name='relat_pacientes'),
    path('relatorios/pdfpacientes', views.RelatPdfPacientes.as_view(),
         name='pdf_pacientes'),
    path('graficos/consultasconvenio', views.ConsConvView.as_view(),
         name='graf_cons_conv'),
    path('graficos/paccidade', views.GrafPacientesCidade.as_view(),
         name='graf_pac_cid'),
]