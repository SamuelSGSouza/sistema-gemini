from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginPageView.as_view(), name='login'),
    path('logout', views.logout_view, name='logout'),

    #secretarios
    path('secretario/home', views.ListarEscolas.as_view(), name='home_secretario'),
    path('secretario/coordenadores', views.ListarCoordenadorGeral.as_view(), name='lista_coordenadores_geral'),
    path('secretario/coordenadores/criar', views.CadastroCoordenadorGeral.as_view(), name='cria_coordenadores_geral'),

    #coordenadores gerais
    path('super_user/dashboard', views.DashboardSuperUser.as_view(), name='home_coordenador_geral'),
    path('cadastro/simulado', views.CreateAvaliacaoView.as_view(), name='coordenador_cadastro_avaliacao'),
    path("coordenador_geral/lista/simulados", views.ListaAvaliacoesView.as_view(), name="coordenador_lista_avaliacoes"),
    path('coordenador_geral/visualizar/resultados/<int:pk>', views.VisualizarResultadoAvaliacao.as_view(), name='coordenador_geral_visualizar_resultados_avaliacao'),

    # path('coordenador_geral/cadastro', views.GeralCreateCoordenadorView.as_view(), name='cadastro_coordenador'),
    
    #coordenadores
    path('coordenador/dashboard', views.DashboardCoordenador.as_view(), name='home_coordenador'),

    path('lista/professores', views.ListaProfessoresView.as_view(), name='coordenador_lista_professores'),
    path('lista/turmas', views.ListaTurmasView.as_view(), name='coordenador_lista_turmas'),
    path('lista/alunos/<int:pk>', views.ListaAlunosView.as_view(), name='coordenador_lista_alunos'),
    path("coordenador/lista/simulados_turma/<int:pk>", views.ListaAvaliacoesTurmaView.as_view(), name="coordenador_lista_avaliacoes_turma"),

    path('cadastro/professor', views.CreateProfessorView.as_view(), name='coordenador_cadastro_professor'),
    path('cadastro/turma', views.CreateTurmaView.as_view(), name='coordenador_cadastro_turma'),
    path('cadastro/aluno', views.CreateAlunoView.as_view(), name='coordenador_cadastro_aluno'),
    path('coordenador/cadastro/gabarito/<int:pk>', views.PreencherGabaritoView.as_view(), name='coordenador_cadastro_gabarito'),
    
    path('edita/professor/<int:pk>', views.EditProfessorView.as_view(), name='coordenador_edita_professor'),
    path('edita/turma/<int:pk>', views.EditTurmaView.as_view(), name='coordenador_edita_turma'),
    path('edita/aluno/<int:pk>', views.EditAlunoView.as_view(), name='coordenador_edita_aluno'),
    
    path('visualizar/simulado/<int:pk>', views.VisualizarAvaliacaoView.as_view(), name='coordenador_visualizar_avaliacao'),


    #professores
    path('professor/lista_alunos', views.ProfessorListView.as_view(), name='home_professor'),
    path('professor/cadastro', views.ProfessorCreateAlunoView.as_view(), name='cadastro_aluno'),
    path('professor/aluno/<int:pk>', views.ProfessorEditAlunoView.as_view(), name='edita_aluno'),



    #geral VisualizarResultadoAvaliacaoEscola
    path('geral/visualizar/resultados/<int:pk>', views.VisualizarResultadoAvaliacaoEscola.as_view(), name='geral_visualizar_resultados_avaliacao'),
    path('geral/visualizar/historico_aluno/<int:pk>', views.VisualizarHistoricoAluno.as_view(), name='geral_visualizar_historico_aluno'),
]
