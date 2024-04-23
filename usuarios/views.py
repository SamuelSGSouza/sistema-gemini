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
from simulados.models import Simulado

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
                print("coordenador")
                return redirect('home_coordenador')
            
            else:
                print("professor")
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
        print("Username: ", username)
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
class CoordenadorView(LoginRequiredMixin):
    login_url = reverse_lazy('login')

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
class CoordenadorDashboard(CoordenadorView, TemplateView):
    template_name = 'usuarios/coordenadores/dashboard.html'

class CoordenadorListaProfessoresView(CoordenadorView, ListView):
    template_name = 'usuarios/coordenadores/lista_professores.html'
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

class CoordenadorCreateProfessorView(CoordenadorView, TemplateView):
    template_name = 'usuarios/coordenadores/cria_professor.html'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        cpf = self.request.POST.get('cpf')
        telefone = self.request.POST.get('telefone')
        email = self.request.POST.get('email')
        username = self.request.POST.get('username')
        senha = self.request.POST.get('senha')
        coordenador = Coordenador.objects.get(user=self.request.user)
        
        context = {
            'nome':nome, 'cpf':cpf, 'telefone':telefone, 'email':email, 'user':username, 'senha':senha}

        #verificando se o username já existe para usuario
        if User.objects.filter(username=username).exists():
            messages.error(self.request, f'O usuário "{username}" não está disponível')
            return render(self.request, self.template_name, context)
        
        #verificando o cpf
        if Professor.objects.filter(cpf=cpf).exists():
            messages.error(self.request, 'Um professor com esse CPF já está cadastrado')
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

        Professor.objects.create(
            nome_completo=nome,
            cpf=cpf,
            telefone=telefone,
            email=email,
            coordenador=coordenador,
            user=user
        )
        messages.success(self.request, 'Professor cadastrado com sucesso!')
        return redirect('coordenador_lista_professores')
    
class CoordenadorEditProfessorView(CoordenadorView, DetailView):
    template_name = 'usuarios/coordenadores/edita_professor.html'
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

class CoordenadorListaAlunosView(CoordenadorView, ListView):
    template_name = 'usuarios/coordenadores/lista_alunos.html'
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
    
class CoordenadorCreateAlunoView(CoordenadorView, TemplateView):
    template_name = 'usuarios/coordenadores/cria_aluno.html'
    
    


    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        turma = Turma.objects.get(id=self.request.session.get('turma_id'))

        Aluno.objects.create(nome=nome, turma=turma)
        messages.success(self.request, 'Aluno cadastrado com sucesso!')
        return redirect('coordenador_lista_alunos', turma.id)
    
class CoordenadorEditAlunoView(CoordenadorView, DetailView):
    template_name = 'usuarios/coordenadores/edita_aluno.html'
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

class CoordenadorListaTurmasView(CoordenadorView, ListView):
    template_name = 'usuarios/coordenadores/lista_turmas.html'
    model = Turma
    login_url = reverse_lazy('login')
    context_object_name = 'turmas'
    paginate_by = 10
    ordering = ['nome']

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        coordenador = Coordenador.objects.get(user=self.request.user)
        escola = coordenador.escola
        qs = qs.filter(escola=escola)
        return qs

    def post(self, *args, **kwargs):
        id = self.request.POST.get('id')
        turma = Turma.objects.get(id=id)
        turma.delete()
        messages.success(self.request, 'Turma deletada com sucesso!')
        return redirect('coordenador_lista_turmas')

class CoordenadorCreateTurmaView(CoordenadorView, TemplateView):
    template_name = 'usuarios/coordenadores/cria_turma.html'

    def post(self, *args, **kwargs):
        nome = self.request.POST.get('nome')
        coordenador = Coordenador.objects.get(user=self.request.user)
        escola = coordenador.escola

        Turma.objects.create(nome=nome, escola=escola)
        messages.success(self.request, 'Turma cadastrada com sucesso!')
        return redirect('coordenador_lista_turmas')
    
class CoordenadorEditTurmaView(CoordenadorView, DetailView):
    template_name = 'usuarios/coordenadores/edita_turma.html'
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
        print(context['turmas_alunos'][0].get('alunos'))    
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
    