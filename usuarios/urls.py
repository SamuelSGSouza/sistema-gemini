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
    path('coordenador_geral/home', views.CoordenadorGeralListView.as_view(), name='home_coordenador_geral'),
    path('coordenador_geral/cadastro', views.CoordenadorGeralCreateCoordenadorView.as_view(), name='cadastro_coordenador'),
    
    #coordenadores
    path('coordenador/dashboard', views.CoordenadorDashboard.as_view(), name='home_coordenador'),

    path('coordenador/lista/professores', views.CoordenadorListaProfessoresView.as_view(), name='coordenador_lista_professores'),
    path('coordenador/lista/turmas', views.CoordenadorListaTurmasView.as_view(), name='coordenador_lista_turmas'),
    path('coordenador/lista/alunos/<int:pk>', views.CoordenadorListaAlunosView.as_view(), name='coordenador_lista_alunos'),
    
    path('coordenador/cadastro/professor', views.CoordenadorCreateProfessorView.as_view(), name='coordenador_cadastro_professor'),
    path('coordenador/cadastro/turma', views.CoordenadorCreateTurmaView.as_view(), name='coordenador_cadastro_turma'),
    path('coordenador/cadastro/aluno', views.CoordenadorCreateAlunoView.as_view(), name='coordenador_cadastro_aluno'),
    
    path('coordenador/edita/professor/<int:pk>', views.CoordenadorEditProfessorView.as_view(), name='coordenador_edita_professor'),
    path('coordenador/edita/turma/<int:pk>', views.CoordenadorEditTurmaView.as_view(), name='coordenador_edita_turma'),
    path('coordenador/edita/aluno/<int:pk>', views.CoordenadorEditAlunoView.as_view(), name='coordenador_edita_aluno'),

    #professores
    path('professor/lista_alunos', views.ProfessorListView.as_view(), name='home_professor'),
    path('professor/cadastro', views.ProfessorCreateAlunoView.as_view(), name='cadastro_aluno'),
    path('professor/aluno/<int:pk>', views.ProfessorEditAlunoView.as_view(), name='edita_aluno'),
]
