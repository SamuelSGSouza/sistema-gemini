from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from simulados.models import *
from collections import defaultdict
import pandas as pd

class LoginPageView(TemplateView):
    template_name = 'base_login.html'

    def post(self, *args, **kwargs):
        email = self.request.POST.get('email-username')
        senha = self.request.POST.get('password')

        user = authenticate(username=email, password=senha)
        if user:
            login(self.request, user)

            self.request.session['nome'] = self.request.user.first_name
            
            

            #verificando se o usuario é secretario
            if Secretario.objects.filter(user=user).exists():
                usuario = Secretario.objects.get(user=user)

                self.request.session['classe'] = "Secretário"
                self.request.session["geral_id"] = usuario.id
                self.request.session["rede"] = usuario.rede
                
                return redirect('home_coordenador_geral')
            
            #verificando se o usuario é coordenador geral
            elif CoordenadorGeral.objects.filter(user=user).exists():
                print("coordenador geral")
                usuario = CoordenadorGeral.objects.get(user=user)

                self.request.session['classe'] = "Coordenador Geral"
                self.request.session["geral_id"] = usuario.id
                self.request.session["rede"] = usuario.secretario.rede
                
                return redirect('home_coordenador_geral')

            elif Coordenador.objects.filter(user=user).exists():
                print("coordenador")
                return redirect('home_coordenador')
            
            else:
                messages.error(self.request, 'Usuário ou senha incorretos')
                logout(self.request)
                return redirect('login')
            
                
        else:
            messages.error(self.request, 'Usuário ou senha incorretos')
            return redirect('login')
        
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            user = self.request.user
            self.request.session['nome'] = self.request.user.first_name
            
            

            #verificando se o usuario é secretario
            if Secretario.objects.filter(user=user).exists():
                usuario = Secretario.objects.get(user=user)

                self.request.session['classe'] = "Secretário"
                self.request.session["geral_id"] = usuario.id
                self.request.session["rede"] = usuario.rede
                
                return redirect('home_coordenador_geral')
            
            #verificando se o usuario é coordenador geral
            elif CoordenadorGeral.objects.filter(user=user).exists():
                print("coordenador geral")
                usuario = CoordenadorGeral.objects.get(user=user)

                self.request.session['classe'] = "Coordenador Geral"
                self.request.session["geral_id"] = usuario.id
                self.request.session["rede"] = usuario.secretario.rede
                
                return redirect('home_coordenador_geral')

            elif Coordenador.objects.filter(user=user).exists():
                print("coordenador")
                return redirect('home_coordenador')
            
            
            else:
                messages.error(self.request, 'Usuário ou senha incorretos')
                logout(self.request)
                return redirect('login')
        return render(self.request, self.template_name)
    
def logout_view(request):
    logout(request)
    return redirect('login')

################ SECRETARIO ################
class SecretarioView(LoginRequiredMixin):
    login_url = reverse_lazy('login')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        secretario = Secretario.objects.filter(user=self.request.user)
        if not secretario.exists():
            return context
        secretario = secretario.first()

        self.request.session['nome'] = str(secretario.nome_completo).split(" ")[0]
        self.request.session['classe'] = "Secretário"
        self.request.session["secretario_id"] = secretario.id
        self.request.session["estado"] = secretario.estado
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
        coordenador_geral = CoordenadorGeral.objects.filter(user=self.request.user)
        if not coordenador_geral.exists():
            return context
        
        coordenador_geral = coordenador_geral.first()
        self.request.session['nome'] = str(coordenador_geral.nome_completo).split(" ")[0]
        self.request.session['classe'] = "Coordenador Geral"
        self.request.session["coordenador_id"] = coordenador_geral.id
        return context

class CoordenadorGeralListView(CoordenadorGeralView, ListView):
    template_name = 'usuarios/superuser/lista_coordenadores.html'
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
    template_name = 'usuarios/superuser/cad_coordenador.html'

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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        coordenador = Coordenador.objects.filter(user=user)
        if not coordenador.exists():
            return context
        
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
        rede = Coordenador.objects.get(user=self.request.user).coordenador_geral.secretario.rede
        print(rede)
        avaliacoes = Simulado.objects.filter(grau_ensino=grau_turma, rede=rede)
        respondidas = self.object.simulados_respondidos.all()
        for avaliacao in avaliacoes:
            if avaliacao in respondidas:
                avaliacao.respondida = True
            else:
                avaliacao.respondida = False
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
class SuperUserGeralBaseView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    #criando redirect para deslogar caso o usuario não seja coordenador
    def dispatch(self, request, *args, **kwargs):
        if not CoordenadorGeral.objects.filter(user=request.user).exists() and not Secretario.objects.filter(user=request.user).exists():
            logout(request)
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
    

class DashboardSuperUser(SuperUserGeralBaseView, TemplateView):
    template_name = 'usuarios/superuser/dashboard.html'
    model = Simulado

    def get_context_data(self, **kwargs):

        #pegando a rede
        if CoordenadorGeral.objects.filter(user=self.request.user).exists():
            coordenador_geral = CoordenadorGeral.objects.get(user=self.request.user)
            rede = coordenador_geral.secretario.rede
        else:
            rede = Secretario.objects.get(user=self.request.user).rede

        #pegando os simulados da rede
        simulados = Simulado.objects.filter(rede=rede)
        context = super().get_context_data(**kwargs)
        questoes = QuestaoReferencia.objects.filter(simulado__in=simulados)
        context['questoes'] = questoes
        respostas =  Resposta.objects.filter(questao_referencia__simulado__in=simulados)
        context['respostas'] = respostas

        #calculando o percentual de acertos
        total_acertos = 0
        for questao in questoes:
            if questao.quantidade_respostas_corretas:
                total_acertos += questao.quantidade_respostas_corretas
            else:
                total_acertos += 0

        total_respostas = respostas.count()
        if total_respostas > 0:
            percentual_acertos = round((total_acertos/total_respostas)*100, 2)
        else:
            percentual_acertos = 0
        context['percentual_acertos'] = percentual_acertos
        context['total_acertos'] = total_acertos
        context['total_respostas'] = respostas.count()

        lista_questoes = []
        for questao in questoes:
            respostas_questao = respostas.filter(questao_referencia=questao)

            questao_dict = {}
            questao_dict["numero"] = questao.numero_questao
            questao_dict["quantidade_respostas"] = respostas_questao.count()
            questao_dict["quantidade_respostas_corretas"] = questao.quantidade_respostas_corretas or 0
            questao_dict["componente"] = questao.questao.componente
            questao_dict["descritor"] = questao.questao.descritor
            questao_dict["unidade_tematica"] = questao.questao.unidade_tematica_texto
            questao_dict["habilidades_abncc"] = questao.questao.habilidades_abncc_texto
            questoes_por_opcao = [
                {"letra": "b", "quantidade": questao.quantidade_respostas_b},
                {"letra": "c", "quantidade": questao.quantidade_respostas_c},
                {"letra": "d", "quantidade": questao.quantidade_respostas_d},
                {"letra": "a", "quantidade": questao.quantidade_respostas_a},
                
                
                
            ]
                        
            #transformando em dict com label_1, data_1, label_2, data_2
            questoes_por_opcao_dict = {}
            for i, opcao in enumerate(questoes_por_opcao):
                questoes_por_opcao_dict[f"label_{i+1}"] = opcao["letra"]
                questoes_por_opcao_dict[f"data_{i+1}"] = opcao["quantidade"]
            questao_dict["questoes_por_opcao"] = questoes_por_opcao_dict

            questao_dict['resposta_correta'] = questao.questao.alternativa_correta
            
            lista_questoes.append(questao_dict)
        context['lista_questoes'] = lista_questoes


        

        # Inicialização do dicionário de escolas
        escolas = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": ""})
        turmas = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": "", "escola": "", "pontuacao_media":""})
        alunos = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": ""})
        # Agrupando as questões por escola e calculando a média de acertos simultaneamente
        for resposta in respostas:
            escola = resposta.aluno.turma.escola
            turma = resposta.aluno.turma
            aluno = resposta.aluno
            escolas[escola]["nome"] = escola.nome
            escolas[escola]["id"] = escola.id
            escolas[escola]["respostas"] += 1

            alunos[aluno]["nome"] = aluno.nome
            alunos[aluno]["id"] = aluno.id
            alunos[aluno]["respostas"] += 1

            turmas[turma]["nome"] = turma.nome
            turmas[turma]["id"] = turma.id
            turmas[turma]["respostas"] += 1
            turmas[turma]["escola"] = escola.nome

            if resposta.acertou:
                escolas[escola]["acertos"] += 1
                alunos[aluno]["acertos"] += 1
                turmas[turma]["acertos"] += 1

        # Calculando percentual de acertos e preparando os dados para ordenação
        for dados in escolas.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)

        for dados in alunos.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)

        for dados in turmas.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)
            dados["pontuacao_media"] = round((dados["acertos"] / dados["respostas"]) * 10, 2)
        
        #inserindo situacao turma
        for turma in turmas.values():
            if turma["percentual_acertos"] < 26:
                turma["situacao"] = "Abaixo do Básico"
            elif turma["percentual_acertos"] < 51:
                turma["situacao"] = "Básico"
            elif turma["percentual_acertos"] < 76:
                turma["situacao"] = "Adequado"
            else:
                turma["situacao"] = "Avançado"

        # Ordenando por percentual de acertos
        escolas_ordenadas = dict(sorted(escolas.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))
        alunos_ordenados = dict(sorted(alunos.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))
        turmas_ordenadas = dict(sorted(turmas.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))

        #transformando em lista
        escolas_ordenadas = list(escolas_ordenadas.values())
        alunos_ordenados = list(alunos_ordenados.values())
        turmas_ordenadas = list(turmas_ordenadas.values())

        context['escolas'] = escolas_ordenadas
        context['alunos'] = alunos_ordenados
        context['turmas'] = turmas_ordenadas
        
        return context
    

class ListaAvaliacoesView(SuperUserGeralBaseView, ListView):
    template_name = 'listar/lista_avaliacao.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'avaliacoes'
    paginate_by = 10
    ordering = ['nome']

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()

        #pegando a rede
        if CoordenadorGeral.objects.filter(user=self.request.user).exists():
            rede = CoordenadorGeral.objects.get(user=self.request.user).secretario.rede
        elif Secretario.objects.filter(user=self.request.user).exists():
            rede = Secretario.objects.get(user=self.request.user).rede
        else:
            rede = None
        qs = qs.filter(rede = rede)
        return qs

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        simulado = Simulado.objects.get(id=id)
        simulado.delete()
        messages.success(self.request, 'Simulado deletado com sucesso!')
        return redirect('coordenador_lista_avaliacoes')

class CreateAvaliacaoView(SuperUserGeralBaseView, TemplateView):
    template_name = 'criar/cria_avaliacao.html'

    def get(self, *args, **kwargs):
        componentes = ComponenteCurricular.objects.all().order_by('componente')
        unidades = UnidadeTematica.objects.all()
        descritores = Descritor.objects.all()
        habilidades_bncc = HabilidadesBNCC.objects.all()
        context = {
            'componentes': componentes,
            'habilidades_bncc': habilidades_bncc,
            'unidades': unidades,
            'descritores': descritores
        }
        return render(self.request, self.template_name, context)

    def post(self, *args, **kwargs):

        rede = CoordenadorGeral.objects.get(user=self.request.user).secretario.rede
       

        simulado = Simulado.objects.create(
            nome=self.request.POST.get('nome'),
            responsavel=self.request.user,
            tipo_simulado="questoes_construidas",
            grau_ensino=self.request.POST.get('grau_ensino'),
            matriz_referencial=self.request.POST.get('matriz_referencial'),
            rede=rede,
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

class VisualizarAvaliacaoView(SuperUserGeralBaseView, DetailView):
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

class VisualizarResultadoAvaliacao(SuperUserGeralBaseView, DetailView):
    template_name = 'usuarios/superuser/visualizar_resultado_avaliacao.html'
    model = Simulado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulado = Simulado.objects.get(id=self.kwargs.get('pk'))
        self.request.session['simulado_id'] = simulado.id
        questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
        context['questoes'] = questoes
        context['simulado'] = simulado
        respostas =  Resposta.objects.filter(questao_referencia__simulado=simulado)
        context['respostas'] = respostas

        #calculando o percentual de acertos
        total_acertos = 0
        for questao in questoes:
            if questao.quantidade_respostas_corretas:
                total_acertos += questao.quantidade_respostas_corretas
            else:
                total_acertos += 0

        total_respostas = respostas.count()
        if total_respostas > 0:
            percentual_acertos = round((total_acertos/total_respostas)*100, 2)
        else:
            percentual_acertos = 0
        context['percentual_acertos'] = percentual_acertos
        context['total_acertos'] = total_acertos
        context['total_respostas'] = respostas.count()

        lista_questoes = []
        for questao in questoes:
            respostas_questao = respostas.filter(questao_referencia=questao)

            questao_dict = {}
            questao_dict["numero"] = questao.numero_questao
            questao_dict["quantidade_respostas"] = respostas_questao.count()
            questao_dict["quantidade_respostas_corretas"] = questao.quantidade_respostas_corretas or 0
            questao_dict["componente"] = questao.questao.componente
            questao_dict["descritor"] = questao.questao.descritor
            questao_dict["unidade_tematica"] = questao.questao.unidade_tematica_texto
            questao_dict["habilidades_abncc"] = questao.questao.habilidades_abncc_texto
            questoes_por_opcao = [
                {"letra": "b", "quantidade": questao.quantidade_respostas_b},
                {"letra": "c", "quantidade": questao.quantidade_respostas_c},
                {"letra": "d", "quantidade": questao.quantidade_respostas_d},
                {"letra": "a", "quantidade": questao.quantidade_respostas_a},
                
                
                
            ]
                        
            #transformando em dict com label_1, data_1, label_2, data_2
            questoes_por_opcao_dict = {}
            for i, opcao in enumerate(questoes_por_opcao):
                questoes_por_opcao_dict[f"label_{i+1}"] = opcao["letra"]
                questoes_por_opcao_dict[f"data_{i+1}"] = opcao["quantidade"]
            questao_dict["questoes_por_opcao"] = questoes_por_opcao_dict

            questao_dict['resposta_correta'] = questao.questao.alternativa_correta
            
            lista_questoes.append(questao_dict)
        context['lista_questoes'] = lista_questoes


        

        # Inicialização do dicionário de escolas
        escolas = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": ""})
        turmas = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": "", "escola": "", "pontuacao_media":""})
        alunos = defaultdict(lambda: {"respostas": 0, "acertos": 0, "nome": "", "id": ""})
        # Agrupando as questões por escola e calculando a média de acertos simultaneamente
        for resposta in respostas:
            escola = resposta.aluno.turma.escola
            turma = resposta.aluno.turma
            aluno = resposta.aluno
            escolas[escola]["nome"] = escola.nome
            escolas[escola]["id"] = escola.id
            escolas[escola]["respostas"] += 1

            alunos[aluno]["nome"] = aluno.nome
            alunos[aluno]["id"] = aluno.id
            alunos[aluno]["respostas"] += 1

            turmas[turma]["nome"] = turma.nome
            turmas[turma]["id"] = turma.id
            turmas[turma]["respostas"] += 1
            turmas[turma]["escola"] = escola.nome

            if resposta.acertou:
                escolas[escola]["acertos"] += 1
                alunos[aluno]["acertos"] += 1
                turmas[turma]["acertos"] += 1

        # Calculando percentual de acertos e preparando os dados para ordenação
        for dados in escolas.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)

        for dados in alunos.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)

        for dados in turmas.values():
            dados["percentual_acertos"] = round((dados["acertos"] / dados["respostas"]) * 100, 2)
            dados["pontuacao_media"] = round((dados["acertos"] / dados["respostas"]) * 10, 2)
        
        #inserindo situacao turma
        for turma in turmas.values():
            if turma["percentual_acertos"] < 26:
                turma["situacao"] = "Abaixo do Básico"
            elif turma["percentual_acertos"] < 51:
                turma["situacao"] = "Básico"
            elif turma["percentual_acertos"] < 76:
                turma["situacao"] = "Adequado"
            else:
                turma["situacao"] = "Avançado"

        # Ordenando por percentual de acertos
        escolas_ordenadas = dict(sorted(escolas.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))
        alunos_ordenados = dict(sorted(alunos.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))
        turmas_ordenadas = dict(sorted(turmas.items(), key=lambda item: item[1]["percentual_acertos"], reverse=True))

        #transformando em lista
        escolas_ordenadas = list(escolas_ordenadas.values())
        alunos_ordenados = list(alunos_ordenados.values())
        turmas_ordenadas = list(turmas_ordenadas.values())

        context['escolas'] = escolas_ordenadas
        context['alunos'] = alunos_ordenados
        context['turmas'] = turmas_ordenadas
        
        return context
    

############# PROFESSOR ################
class ProfessorView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
         

        professor = Professor.objects.filter(user=self.request.user)
        if not professor.exists():
            return context
        
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
        professor = Professor.objects.filter(user=self.request.user)
        if not professor.exists():
            return context
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


############# GERAL ################
class VisualizarResultadoAvaliacaoEscola(TemplateView, LoginRequiredMixin):
    login_url = reverse_lazy('login')
    template_name = 'visualizar/resultado_avaliacao_escola.html'

    def get(self, *args, **kwargs):
        escola_id = self.kwargs.get('pk')
        simulado_id = self.request.session.get('simulado_id') or self.request.GET.get('simulado_id')
        escola = Escola.objects.get(id=escola_id)
        simulado = Simulado.objects.get(id=simulado_id)
        questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
        respostas = Resposta.objects.filter(questao_referencia__simulado=simulado, aluno__turma__escola=escola)
        total_acertos = 0
        for reposta in respostas:
            if reposta.acertou:
                total_acertos += 1

        percentual_acertos = round((total_acertos/respostas.count())*100, 2)
        total_respostas = respostas.count()

        lista_questoes = []
        for questao in questoes:
            respostas_questao = respostas.filter(questao_referencia=questao)

            questao_dict = {}
            questao_dict["numero"] = questao.numero_questao
            questao_dict["quantidade_respostas"] = respostas_questao.count()
            questao_dict["quantidade_respostas_corretas"] = respostas_questao.filter(acertou=True).count()
            questao_dict["componente"] = questao.questao.componente
            questao_dict["descritor"] = questao.questao.descritor
            questao_dict["unidade_tematica"] = questao.questao.unidade_tematica_texto
            questao_dict["habilidades_abncc"] = questao.questao.habilidades_abncc_texto

            questoes_por_opcao = [
                {"letra": "b", "quantidade": respostas_questao.filter(resposta='b').count()},
                {"letra": "c", "quantidade": respostas_questao.filter(resposta='c').count()},
                {"letra": "d", "quantidade": respostas_questao.filter(resposta='d').count()},
                {"letra": "a", "quantidade": respostas_questao.filter(resposta='a').count()},
            ]
            #transformando em dict com label_1, data_1, label_2, data_2
            questoes_por_opcao_dict = {}
            for i, opcao in enumerate(questoes_por_opcao):
                questoes_por_opcao_dict[f"label_{i+1}"] = opcao["letra"]
                questoes_por_opcao_dict[f"data_{i+1}"] = opcao["quantidade"]
            questao_dict["questoes_por_opcao"] = questoes_por_opcao_dict

            questao_dict['resposta_correta'] = questao.questao.alternativa_correta
            lista_questoes.append(questao_dict)

        #alunos
        alunos = Aluno.objects.filter(turma__escola=escola)
        alunos_dict = []
        for aluno in alunos:
            respostas_aluno = respostas.filter(aluno=aluno)
            total_acertos_aluno = respostas_aluno.filter(acertou=True).count()
            if respostas_aluno.count() == 0:
                percentual_acertos_aluno = 0
            else:
                percentual_acertos_aluno = round((total_acertos_aluno/respostas_aluno.count())*100, 2)
            
            pontuacao_aluno = round(percentual_acertos_aluno/10, 1)

            #definindo a situacao do aluno
            if percentual_acertos_aluno < 26:
                situacao_aluno = "Abaixo do Básico"
            elif percentual_acertos_aluno < 51:
                situacao_aluno = "Básico"
            elif percentual_acertos_aluno < 76:
                situacao_aluno = "Adequado"
            else:
                situacao_aluno = "Avançado"

            alunos_dict.append({
                'nome': aluno.nome,
                "id": aluno.id,
                'percentual_acertos': percentual_acertos_aluno,
                'total_acertos': total_acertos_aluno,
                'total_respostas': respostas_aluno.count(),
                'pontuacao': pontuacao_aluno,
                'situacao': situacao_aluno 
            })

        #ordenando alunos por percentual de acertos
        alunos_dict = sorted(alunos_dict, key=lambda x: x['percentual_acertos'], reverse=True)
        

            
        context = {
            'questoes': lista_questoes,
            'simulado': simulado,
            'percentual_acertos': percentual_acertos,
            'total_acertos': total_acertos,
            'total_respostas': total_respostas,
            'escola': escola,
            'alunos': alunos_dict
        }
        return render(self.request, self.template_name, context)

class VisualizarResultadoAvaliacaoTurma(TemplateView, LoginRequiredMixin):
    login_url = reverse_lazy('login')
    template_name = 'visualizar/resultado_avaliacao_turma.html'

    def get(self, *args, **kwargs):
        turma_id = self.kwargs.get('pk')
        simulado_id = self.request.session.get('simulado_id') or self.request.GET.get('simulado_id')
        turma = Turma.objects.get(id=turma_id)
        simulado = Simulado.objects.get(id=simulado_id)
        questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
        respostas = Resposta.objects.filter(questao_referencia__simulado=simulado, aluno__turma=turma)
        total_acertos = 0
        for reposta in respostas:
            if reposta.acertou:
                total_acertos += 1

        percentual_acertos = round((total_acertos/respostas.count())*100, 2)
        total_respostas = respostas.count()

        lista_questoes = []
        for questao in questoes:
            respostas_questao = respostas.filter(questao_referencia=questao)

            questao_dict = {}
            questao_dict["numero"] = questao.numero_questao
            questao_dict["quantidade_respostas"] = respostas_questao.count()
            questao_dict["quantidade_respostas_corretas"] = respostas_questao.filter(acertou=True).count()
            questao_dict["componente"] = questao.questao.componente
            questao_dict["descritor"] = questao.questao.descritor
            questao_dict["unidade_tematica"] = questao.questao.unidade_tematica_texto
            questao_dict["habilidades_abncc"] = questao.questao.habilidades_abncc_texto

            questoes_por_opcao = [
                {"letra": "b", "quantidade": respostas_questao.filter(resposta='b').count()},
                {"letra": "c", "quantidade": respostas_questao.filter(resposta='c').count()},
                {"letra": "d", "quantidade": respostas_questao.filter(resposta='d').count()},
                {"letra": "a", "quantidade": respostas_questao.filter(resposta='a').count()},
            ]
            #transformando em dict com label_1, data_1, label_2, data_2
            questoes_por_opcao_dict = {}
            for i, opcao in enumerate(questoes_por_opcao):
                questoes_por_opcao_dict[f"label_{i+1}"] = opcao["letra"]
                questoes_por_opcao_dict[f"data_{i+1}"] = opcao["quantidade"]
            questao_dict["questoes_por_opcao"] = questoes_por_opcao_dict

            questao_dict['resposta_correta'] = questao.questao.alternativa_correta
            lista_questoes.append(questao_dict)

        #alunos
        alunos = Aluno.objects.filter(turma=turma)
        alunos_dict = []

        for aluno in alunos:
            respostas_aluno = respostas.filter(aluno=aluno)
            total_acertos_aluno = respostas_aluno.filter(acertou=True).count()
            if respostas_aluno.count() == 0:
                percentual_acertos_aluno = 0
            else:
                percentual_acertos_aluno = round((total_acertos_aluno/respostas_aluno.count())*100, 2)
            
            pontuacao_aluno = round(percentual_acertos_aluno/10, 1)

            #definindo a situacao do aluno
            if percentual_acertos_aluno < 26:
                situacao_aluno = "Abaixo do Básico"
            elif percentual_acertos_aluno < 51:
                situacao_aluno = "Básico"
            elif percentual_acertos_aluno < 76:
                situacao_aluno = "Adequado"
            else:
                situacao_aluno = "Avançado"

            alunos_dict.append({
                'nome': aluno.nome,
                "id": aluno.id,
                'percentual_acertos': percentual_acertos_aluno,
                'total_acertos': total_acertos_aluno,
                'total_respostas': respostas_aluno.count(),
                'pontuacao': pontuacao_aluno,
                'situacao': situacao_aluno 
            })

        #ordenando alunos por percentual de acertos
        alunos_dict = sorted(alunos_dict, key=lambda x: x['percentual_acertos'], reverse=True)
        

            
        context = {
            'questoes': lista_questoes,
            'simulado': simulado,
            'percentual_acertos': percentual_acertos,
            'total_acertos': total_acertos,
            'total_respostas': total_respostas,
            'alunos': alunos_dict,
            'turma': turma
        }
        return render(self.request, self.template_name, context)  

class VisualizarHistoricoAluno(TemplateView, LoginRequiredMixin):
    template_name = 'visualizar/historico_aluno.html'
    login_url = reverse_lazy('login')

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        id_aluno = kwargs.get('pk')
        aluno = Aluno.objects.get(id=id_aluno)

        #pegando as avaliações que o aluno respondeu
        respostas = Resposta.objects.filter(aluno=aluno)
        simulados = []
        for resposta in respostas:
            simulado = resposta.questao_referencia.simulado
            if simulado not in simulados:
                simulados.append(simulado)

        #contando percentual de acerto por simulado
        simulados_dict = []
        for simulado in simulados:
            respostas_simulado = respostas.filter(questao_referencia__simulado=simulado)
            total_acertos = respostas_simulado.filter(acertou=True).count()
            percentual_acertos = round((total_acertos/respostas_simulado.count())*100, 2)
            simulados_dict.append({
                'simulado': simulado,
                'percentual_acertos': percentual_acertos,
                'total_acertos': total_acertos,
                'total_respostas': respostas_simulado.count(),
                'criacao': simulado.criacao
            })

        #ordenando simulados por data de criação
        simulados_dict = sorted(simulados_dict, key=lambda x: x['criacao'], reverse=True)


        context = {
            'aluno': aluno,
            'simulados': simulados_dict
        }
        
        return render(request, self.template_name, context)

class CadastrarAlunosLote(TemplateView, LoginRequiredMixin):
    template_name = 'cadastrar_alunos_lote.html'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        for escola in Escola.objects.all():
            print(escola.rede)
        #verificando se é superuser
        user = request.user
        if not user.is_superuser:
            logout(request)
            return redirect('login')
        
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        #pegando o arquivo csv
        csv_file = request.FILES['file']


        df = pd.read_csv(csv_file, sep=";")
        df_falhas = []

        #iterando sobre o dataframe
        for index, row in df.iterrows():
            rede = row['REDE']
            escola = row['ESCOLA']
            turma = row['TURMA']
            aluno = row['NOME_DO_ALUNO']

            
            #pegando rede
            rede_db = Escola.objects.filter(rede=rede).first()
            if not rede_db:
                df_falhas.append({
                    'rede': rede,
                    'escola': escola,
                    'turma': turma,
                    'aluno': aluno,
                    'motivo': 'Rede não encontrada'
                })
                continue

            #pegando escola
            escola_db = Escola.objects.filter(nome=escola, rede=rede).first()
            if not escola_db:
                df_falhas.append({
                    'rede': rede,
                    'escola': escola,
                    'turma': turma,
                    'aluno': aluno,
                    'motivo': 'Escola não encontrada'
                })
                continue

            #pegando turma
            turma_db = Turma.objects.filter(nome=turma, escola=escola_db).first()
            if not turma_db:
                df_falhas.append({
                    'rede': rede,
                    'escola': escola,
                    'turma': turma,
                    'aluno': aluno,
                    'motivo': 'Turma não encontrada'
                })
                continue

            #criando aluno
            Aluno.objects.create(nome=aluno, turma=turma_db)

        #retornando as falhas em um arquivo csv
        # criando um dataframe com as falhas
        df_falhas = pd.DataFrame(df_falhas)
        #criando um arquivo csv
        df_falhas.to_csv('falhas.csv', index=False)
        #retornando o arquivo csv
        with open('falhas.csv', 'rb') as f:
            response = HttpResponse(f, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=falhas.csv'
            return response    