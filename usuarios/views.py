from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from simulados.models import *

#cordenadores
class LoginPageView(TemplateView):
    template_name = 'base_login.html'

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email-username')
        senha = self.request.POST.get('password')

        user = authenticate(username=email, password=senha)
        if user:
            login(self.request, user)

            #verificando se o usuario é secretario
            if Secretario.objects.filter(user=user).exists():
                return redirect('home_secretario')
            
            #verificando se o usuario é coordenador geral
            elif CoordenadorGeral.objects.filter(user=user).exists():
                return redirect('home_coordenador_geral')

            elif Coordenador.objects.filter(user=user).exists():
                return redirect('home_coordenador')
            
            elif Professor.objects.filter(user=user).exists():
                return redirect('home_professor')
            
                
        else:
            messages.error(self.request, 'Usuário ou senha incorretos')
            return redirect('login')
        
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            email = self.request.user.username
            #verificando se o usuario é coordenador
            if Coordenador.objects.filter(email=email).exists():
                return redirect('home_coordenador')
            
            else:
                return redirect('home_professor')
        return render(self.request, self.template_name)
    
def logout_view(request):
    logout(request)
    return redirect('login')

################ SECRETARIO ################
class SecretarioView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['nome'] = str(Secretario.objects.get(user=self.request.user).nome_completo).split(" ")[0]
        self.request.session['classe'] = "Secretário"
        self.request.session["secretario_id"] = Secretario.objects.get(user=self.request.user).id
        self.request.session["estado"] = Secretario.objects.get(user=self.request.user).estado
        return context

class ListarEscolas(SecretarioView, ListView):
    template_name = 'usuarios/secretarios/lista_escolas.html'
    model = Escola
    login_url = reverse_lazy('login')
    context_object_name = 'escolas'
    ordering = ['nome']
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        estado = Secretario.objects.get(user=self.request.user).estado
        return qs.filter(estado=estado)

class ListarCoordenadorGeral(SecretarioView, ListView):
    template_name = 'usuarios/secretarios/lista_coordenadores.html'
    model = CoordenadorGeral
    login_url = reverse_lazy('login')
    context_object_name = 'coordenadores'
    ordering = ['nome_completo']
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        secretario = Secretario.objects.get(user=self.request.user)
        qs = qs.filter(secretario=secretario)
        return qs

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        coordenador = Coordenador.objects.get(id=id)
        coordenador.delete()
        messages.success(self.request, 'Coordenador deletado com sucesso!')
        return redirect('home_secretario')

class CadastroCoordenadorGeral(SecretarioView, TemplateView):
    template_name = 'usuarios/secretarios/cad_coordenador.html'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        cpf = self.request.POST.get('cpf')
        telefone = self.request.POST.get('telefone')
        email = self.request.POST.get('email')
        username = self.request.POST.get('username')
        senha = self.request.POST.get('senha')
        secretario = Secretario.objects.get(user=self.request.user)
        
        context = {
            'nome_coordenador':nome.strip(), 
            'cpf_coordenador':cpf.strip(), 
            'telefone_coordenador':telefone.strip(), 
            'email_coordenador':email.strip(), 
            'user_coordenador':username.strip(),
            'senha_coordenador':senha.strip()
            }

        #verificando se o username já existe para usuario
        if User.objects.filter(username=username).exists():
            messages.error(self.request, f'O usuário "{username}" já existe')
            return render(self.request, self.template_name, context)
        
        #verificando o cpf
        if CoordenadorGeral.objects.filter(cpf=cpf).exists():
            messages.error(self.request, 'CPF já cadastrado')
            return render(self.request, self.template_name, context)
        
        #criando user
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=senha, 
            first_name=nome.split(' ')[0],
            last_name=nome.split(' ')[-1]
            )
        user.save()
        
        
        CoordenadorGeral.objects.create(
            nome_completo=nome, 
            cpf=cpf,
            email=email,
            telefone=telefone,
            secretario=secretario,
            user=user)
        messages.success(self.request, 'Coordenador cadastrado com sucesso!')
        return redirect('lista_coordenadores_geral')

################ COORDENADOR GERAL ################
class CoordenadorGeralView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.request.session['nome'] = str(CoordenadorGeral.objects.get(user=self.request.user).nome_completo).split(" ")[0]
        self.request.session['classe'] = "Coordenador Geral"
        self.request.session["coordenador_id"] = CoordenadorGeral.objects.get(user=self.request.user).id
        return context

class CoordenadorGeralListView(CoordenadorGeralView, ListView):
    template_name = 'usuarios/coordenadores_gerais/lista_coordenadores.html'
    model = Coordenador
    login_url = reverse_lazy('login')
    context_object_name = 'coordenadores'
    ordering = ['nome_completo']
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        secretario = CoordenadorGeral.objects.get(user=self.request.user).secretario
        qs = qs.filter(coordenador_geral__secretario=secretario)
        return qs
    
class CoordenadorGeralCreateCoordenadorView(CoordenadorGeralView, TemplateView):
    template_name = 'usuarios/coordenadores_gerais/cad_coordenador.html'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        cpf = self.request.POST.get('cpf')
        telefone = self.request.POST.get('telefone')
        email = self.request.POST.get('email')
        username = self.request.POST.get('username')
        senha = self.request.POST.get('senha')
        coordenador_geral = CoordenadorGeral.objects.get(user=self.request.user)
        
        context = {
            'nome_coordenador':nome, 
            'cpf_coordenador':cpf, 
            'telefone_coordenador':telefone, 
            'email_coordenador':email, 
            'user_coordenador':username, 
            'senha_coordenador':senha
        }

        #verificando se o username já existe para usuario
        if User.objects.filter(username=username).exists():
            messages.error(self.request, f'O usuário "{username}" já existe')
            return render(self.request, self.template_name, context)
        
        #verificando o cpf
        if Coordenador.objects.filter(cpf=cpf).exists():
            messages.error(self.request, 'CPF já cadastrado')
            return render(self.request, self.template_name, context)
        
        #criando user
        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=senha, 
            first_name=nome.split(' ')[0],
            last_name=nome.split(' ')[-1]
            )
        
        Coordenador.objects.create(
            nome_completo=nome, 
            cpf=cpf,
            email=email,
            telefone=telefone,
            coordenador_geral=coordenador_geral,
            user=user
        )
        messages.success(self.request, 'Coordenador cadastrado com sucesso!')
        user.save()

        return redirect('home_coordenador_geral')

############# COORDENADOR ################
class CoordenadorBaseView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    #criando redirect para deslogar caso o usuario não seja coordenador
    def dispatch(self, request, *args, **kwargs):
        if not Coordenador.objects.filter(user=request.user).exists():
            logout(request)
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        self.request.session['nome'] = self.request.user.first_name
        self.request.session['classe'] = "Coordenador"
        self.request.session["coordenador_id"] = Coordenador.objects.get(user=user).id

        coordenador = Coordenador.objects.get(user=self.request.user)
        escola = coordenador.escola
        turmas = Turma.objects.filter(escola=escola)
        context['turmas'] = turmas
        context['escola'] = escola
        return context
    
class DashboardCoordenador(CoordenadorBaseView, TemplateView):
    template_name = 'usuarios/coordenadores/dashboard.html'

class ListaProfessoresView(CoordenadorBaseView, ListView):
    template_name = 'listar/lista_professores.html'
    model = Professor
    login_url = reverse_lazy('login')
    context_object_name = 'professores'
    paginate_by = 10
    ordering = ['nome_completo']
    
    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(coordenador=self.request.user.coordenador)
        return qs

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        professor = Professor.objects.get(id=id)
        professor.delete()
        messages.success(self.request, 'Professor deletado com sucesso!')
        return redirect('coordenador_lista_professores')

class CreateProfessorView(CoordenadorBaseView, DetailView):
    template_name = 'editar/edita_professor.html'
    model = Professor
    context_object_name = 'professor'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        username = self.request.POST.get('username')
        email = self.request.POST.get('email')
        cpf = self.request.POST.get('cpf')
        telefone = self.request.POST.get('telefone')
        senha = self.request.POST.get('senha') or None
        id = self.request.POST.get('id')

        #update
        professor = Professor.objects.get(id=id)
        user = professor.user

        user.first_name = nome.split(' ')[0]
        user.last_name = nome.split(' ')[-1]
        user.email = email
        if senha:
            user.set_password(senha)
        user.save()

        professor.nome_completo = nome
        professor.email = email
        professor.cpf = cpf
        professor.telefone = telefone

        professor.save()
        messages.success(self.request, 'Professor editado com sucesso!')
        
        return redirect('coordenador_lista_professores')

class EditProfessorView(CoordenadorBaseView, DetailView):
    template_name = 'editar/edita_professor.html'
    model = Professor
    context_object_name = 'professor'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        username = self.request.POST.get('username')
        email = self.request.POST.get('email')
        cpf = self.request.POST.get('cpf')
        telefone = self.request.POST.get('telefone')
        senha = self.request.POST.get('senha') or None
        id = self.request.POST.get('id')

        #update
        professor = Professor.objects.get(id=id)
        user = professor.user

        user.first_name = nome.split(' ')[0]
        user.last_name = nome.split(' ')[-1]
        user.email = email
        if senha:
            user.set_password(senha)
        user.save()

        professor.nome_completo = nome
        professor.email = email
        professor.cpf = cpf
        professor.telefone = telefone

        professor.save()
        messages.success(self.request, 'Professor editado com sucesso!')
        
        return redirect('coordenador_lista_professores')



class ListaAlunosView(CoordenadorBaseView, ListView):
    template_name = 'listar/lista_alunos.html'
    model = Aluno
    login_url = reverse_lazy('login')
    context_object_name = 'alunos'
    paginate_by = 10
    ordering = ['nome']

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        coordenador = Coordenador.objects.get(user=self.request.user)
        escola = coordenador.escola
        qs = qs.filter(turma__escola=escola)

        turma_id = self.kwargs.get('pk')
        if turma_id:
            qs = qs.filter(turma=turma_id)
            self.request.session['turma_id'] = turma_id
        return qs
    

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        aluno = Aluno.objects.get(id=id)
        aluno.delete()
        messages.success(self.request, 'Aluno deletado com sucesso!')
        return redirect('coordenador_lista_alunos', aluno.turma.id)
    
class CreateAlunoView(CoordenadorBaseView, TemplateView):
    template_name = 'criar/cria_aluno.html'
    
    


    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        turma = Turma.objects.get(id=self.request.session.get('turma_id'))

        Aluno.objects.create(nome=nome, turma=turma)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return redirect('coordenador_lista_alunos', turma.id)
    
class EditAlunoView(CoordenadorBaseView, DetailView):
    template_name = 'editar/edita_aluno.html'
    model = Aluno
    context_object_name = 'aluno'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        turma = Turma.objects.get(id=self.request.session.get('turma_id'))
        id = self.request.POST.get('idAluno')

        aluno = Aluno.objects.get(id=id)
        aluno.nome = nome
        aluno.turma = turma
        aluno.save()
        messages.success(self.request, 'Aluno editado com sucesso!')
        
        return redirect('coordenador_lista_alunos', turma.id)


class ListaTurmasView(CoordenadorBaseView, ListView):
    template_name = 'listar/lista_turmas.html'
    model = Turma
    login_url = reverse_lazy('login')
    context_object_name = 'turmas'
    paginate_by = 10
    ordering = ['nome']

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(escola=self.request.user.coordenador.escola)

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        turma = Turma.objects.filter(id=id)
        if turma.exists():
            turma = turma[0]
            turma.delete()
            messages.success(self.request, 'Turma deletada com sucesso!')
            return redirect('coordenador_lista_turmas')
        messages.error(self.request, 'Turma não encontrada')
        return redirect('coordenador_lista_turmas')

class CreateTurmaView(CoordenadorBaseView, TemplateView):
    template_name = 'criar/cria_turma.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nome_escola'] = self.request.user.coordenador.escola.nome
        return context

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        grau = self.request.POST.get('grau')

        Turma.objects.create(nome=nome, escola=self.request.user.coordenador.escola, grau=grau)
        messages.success(self.request, 'Turma cadastrada com sucesso!')
        return redirect('coordenador_lista_turmas')
    
class EditTurmaView(CoordenadorBaseView, DetailView):
    template_name = 'editar/edita_turma.html'
    model = Turma
    context_object_name = 'turma'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['idTurma'] = self.kwargs.get('pk')
        context['turma'] = Turma.objects.get(id=self.kwargs.get('pk'))
        return context

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        id = self.request.POST.get('idTurma')

        turma = Turma.objects.get(id=id)
        turma.nome = nome
        turma.save()
        messages.success(self.request, 'Turma editada com sucesso!')
        
        return redirect('coordenador_lista_turmas')

class ListaAvaliacoesTurmaView(CoordenadorBaseView, DetailView):
    template_name = 'usuarios/coordenadores/lista_avaliacoes_turma.html'
    model = Turma
    login_url = reverse_lazy('login')
    context_object_name = 'turma'
    paginate_by = 10
    ordering = ['nome']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grau_turma = self.object.grau
        avaliacoes = Simulado.objects.filter(grau_ensino=grau_turma)
        respondidas = self.object.simulados_respondidos.all()
        avaliacoes = [avaliacao for avaliacao in avaliacoes if avaliacao not in respondidas]
        context['avaliacoes'] = avaliacoes

        self.request.session['turma_id'] = self.object.id
        return context

class PreencherGabaritoView(CoordenadorBaseView, DetailView):
    template_name = 'usuarios/coordenadores/preencher_gabarito_avaliacao.html'
    model = Simulado
    context_object_name = 'avaliacao'

    def get_context_data(self, **kwargs):
        if self.request.method == 'GET':
            context = super().get_context_data(**kwargs)
            simulado = self.object
            self.request.session['simulado_id'] = simulado.id
            questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
            context['questoes'] = questoes
            context['simulado'] = simulado
            context["turma"] = Turma.objects.get(id=self.request.session.get('turma_id')) 
            context["alunos"] = Aluno.objects.filter(turma=context["turma"])
            return context
        return super().get_context_data(**kwargs)

    def post(self, *args, **kwargs):
        #pegando todas as respostas com resposta_questao_
        for key, value in self.request.POST.items():
            if 'resposta_questao_' in key:
                aluno_id = key.split('_')[-1]
                questao_id = key.split('_')[-2]
                questao = QuestaoReferencia.objects.get(id=questao_id)
                alternativa_correta = questao.questao.alternativa_correta
                alternativa_selecionada = value
                acertou = True if alternativa_correta == alternativa_selecionada else False
                Resposta.objects.create(
                    questao_referencia=questao,
                    resposta=alternativa_selecionada,
                    aluno=Aluno.objects.get(id=aluno_id),
                    acertou=acertou
                )
                if acertou:
                    if not questao.quantidade_respostas_corretas:
                        questao.quantidade_respostas_corretas = 0
                    questao.quantidade_respostas_corretas += 1

                if alternativa_selecionada == 'a':
                    if not questao.quantidade_respostas_a:
                        questao.quantidade_respostas_a = 0
                    questao.quantidade_respostas_a += 1
                elif alternativa_selecionada == 'b':
                    if not questao.quantidade_respostas_b:
                        questao.quantidade_respostas_b = 0
                    questao.quantidade_respostas_b += 1
                elif alternativa_selecionada == 'c':
                    if not questao.quantidade_respostas_c:
                        questao.quantidade_respostas_c = 0
                    questao.quantidade_respostas_c += 1
                elif alternativa_selecionada == 'd':
                    if not questao.quantidade_respostas_d:
                        questao.quantidade_respostas_d = 0
                    questao.quantidade_respostas_d += 1

                questao.save()

        #adicionando o simulado a turma
        turma = Turma.objects.get(id=self.request.session.get('turma_id'))
        turma.simulados_respondidos.add(Simulado.objects.get(id=self.request.session.get('simulado_id')))
        turma.save()
        messages.success(self.request, 'Gabarito preenchido com sucesso!')
        return redirect('coordenador_lista_turmas')


############# COORDENADOR GERAL ################
class CoordenadorGeralBaseView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    #criando redirect para deslogar caso o usuario não seja coordenador
    def dispatch(self, request, *args, **kwargs):
        if not CoordenadorGeral.objects.filter(user=request.user).exists():
            logout(request)
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        self.request.session['nome'] = self.request.user.first_name
        self.request.session['classe'] = "Coordenador Geral"
        self.request.session["coordenador_geral_id"] = CoordenadorGeral.objects.get(user=user).id
        return context

class DashboardCoordenadorGeral(CoordenadorGeralBaseView, TemplateView):
    template_name = 'usuarios/coordenadores_gerais/dashboard.html'

class ListaAvaliacoesView(CoordenadorGeralBaseView, ListView):
    template_name = 'listar/lista_avaliacao.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'avaliacoes'
    paginate_by = 10
    ordering = ['nome']

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(responsavel=self.request.user)
        return qs

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        simulado = Simulado.objects.get(id=id)
        simulado.delete()
        messages.success(self.request, 'Simulado deletado com sucesso!')
        return redirect('coordenador_lista_avaliacoes')

class CreateAvaliacaoView(CoordenadorGeralBaseView, TemplateView):
    template_name = 'criar/cria_avaliacao.html'

    def post(self, *args, **kwargs):
        simulado = Simulado.objects.create(
            nome=self.request.POST.get('nome'),
            responsavel=self.request.user,
            tipo_simulado="questoes_construidas",
            grau_ensino=self.request.POST.get('grau_ensino'),
            matriz_referencial=self.request.POST.get('matriz_referencial'),
        )

        questoes = self.request.POST.get('questoes')
        if questoes:
            questoes = eval(questoes)
        
        for numero_questao, questao in enumerate(questoes):
            questao = Questao.objects.create(
                unidade_tematica_texto=questao["unidade_tematica"],
                habilidades_abncc_texto=questao["habilidades_abncc"],
                descritor=questao["descritor"],
                alternativa_correta=questao["alternativa_correta"],
                componente=questao["componente"],
            )



            QuestaoReferencia.objects.create(
                simulado = simulado,
                numero_questao = numero_questao+1,
                questao = questao,
            )

        messages.success(self.request, 'Avaliação cadastrada com sucesso!')
        return redirect('coordenador_lista_avaliacoes')

class VisualizarAvaliacaoView(CoordenadorGeralBaseView, DetailView):
    template_name = 'visualizar/ver_avaliacao.html'
    model = Simulado
    context_object_name = 'avaliacao'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulado = Simulado.objects.get(id=self.kwargs.get('pk'))
        questoes = QuestaoReferencia.objects.filter(simulado=simulado)
        context['questoes'] = questoes
        context['simulado'] = simulado
        return context

############# PROFESSOR ################
class ProfessorView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         

        professor = Professor.objects.get(user=self.request.user)
        coordenador = professor.coordenador
        escola = Escola.objects.get(Coordenador=coordenador)
        turmas = escola.turmas
        turmas = turmas.split(';')
        turmas = [turma.strip() for turma in turmas]
        context['turmas'] = turmas

        self.request.session['nome'] = self.request.user.first_name
        self.request.session['classe'] = "Professor"
        self.request.session["professor_id"] = professor.id
        
        return context

class AlunoView(ProfessorView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['template_aluno'] = "active"
        return context

class SimuladoView(ProfessorView):
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['template_simulado'] = "active"
            return context
        
class ProfessorListView(AlunoView, ListView):
    template_name = 'usuarios/professores/lista_alunos.html'
    model = Aluno
    login_url = reverse_lazy('login')
    context_object_name = 'alunos'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turmas = []
        professor = Professor.objects.get(user=self.request.user)
        coordenador = professor.coordenador
        escola = Escola.objects.get(Coordenador=coordenador)
        turmas = escola.turmas
        turmas = turmas.split(';')
        turmas = [turma.strip() for turma in turmas if turma != '']

        #separando os alunos por turma
        turmas_alunos = []
        for turma in turmas:
            turmas_g = {}
            alunos = []
            a = Aluno.objects.filter(turma=turma, professor=professor)
            for al in a:
                alunos.append(al)
            turmas_g["alunos"] = alunos
            turmas_g["turma"] = turma
            turmas_alunos.append(turmas_g)
        context['turmas_alunos'] = turmas_alunos
        return context

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        aluno = Aluno.objects.get(id=id)
        aluno.delete()
        messages.success(self.request, 'Aluno deletado com sucesso!')
        return redirect('home_professor')
    
class ProfessorCreateAlunoView(AlunoView, TemplateView):
    template_name = 'usuarios/professores/cria_aluno.html'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        turma = self.request.POST.get('turma')
        professor = Professor.objects.get(user=self.request.user)
        coordenador = professor.coordenador
        escola = Escola.objects.get(Coordenador=coordenador)

        Aluno.objects.create(nome=nome, turma=turma, professor=professor, escola=escola)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return redirect('home_professor')
        
class ProfessorEditAlunoView(AlunoView, DetailView):
    template_name = 'usuarios/professores/edita_aluno.html'
    model = Aluno
    context_object_name = 'aluno'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        turma = self.request.POST.get('turma')
        id = self.request.POST.get('idAluno')

        aluno = Aluno.objects.get(id=id)
        aluno.nome = nome
        aluno.turma = turma
        aluno.save()
        messages.success(self.request, 'Aluno editado com sucesso!')
        
        return redirect('home_professor')
    