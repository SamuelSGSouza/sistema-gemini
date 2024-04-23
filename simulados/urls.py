from django.urls import path
from . import views

urlpatterns = [
    path('', views.SimuladoListView.as_view(), name='lista_simulados'),
    path('simulado_construido/', views.ConstruirSimulado.as_view(), name='construir_simulado'),
    path("cadastrar_simulado/", views.CadastrarSimulado.as_view(), name="cadastrar_simulado"),
    path('visualizar_simulado/<int:pk>/', views.VisualizarSimulado.as_view(), name='visualizar_simulado'),
    path('preenche_gabarito/<int:pk>/', views.PreencheGabarito.as_view(), name='preenche_gabarito'),
    path('visualizar_relatorio/<int:pk>/', views.VisualizarRelatorio.as_view(), name='visualizar_relatorio'),

    path("simulado_proficiencia/", views.SimuladoProficiencia.as_view(), name="simulado_proficiencia"),
]