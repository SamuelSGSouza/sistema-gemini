from typing import Any
from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, TemplateView
from usuarios.views import SimuladoView
from .models import *
from django.urls import reverse_lazy
from usuarios.models import *
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q

class SimuladoListView(ListView):
    template_name = 'simulados/lista_simulados.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'simulados'
    paginate_by = 10
    
    def get_queryset(self) -> QuerySet[Any]:
        


        classe = self.request.session.get('classe')
        qs = super().get_queryset()
        if not classe:
            pass
        
        if classe == 'Professor':
            estado = Professor.objects.get(user=self.request.user).coordenador.coordenador_geral.secretario.estado
            qs = qs.filter(
                Q(tipo_simulado='questoes_gerais', estado=estado) | Q(responsavel=self.request.user)
            )
        elif classe == 'Coordenador':
            estado = Coordenador.objects.get(user=self.request.user).coordenador_geral.secretario.estado
            qs = qs.filter(tipo_simulado='questoes_gerais', estado=estado)
        elif classe == 'Coordenador Geral' or classe == 'Secretário':
            if CoordenadorGeral.objects.filter(user=self.request.user).exists():
                estado = CoordenadorGeral.objects.get(user=self.request.user).secretario.estado
            else:
                estado = Secretario.objects.get(user=self.request.user).estado
            qs = qs.filter(tipo_simulado='questoes_gerais',estado=estado)
            for simulado in qs:
                total_respostas = 0
                total_acertos = 0
                questoes = QuestaoReferencia.objects.filter(simulado=simulado)
                for questao in questoes:
                    respostas = Resposta.objects.filter(questao_referencia=questao)
                    for resposta in respostas:
                        total_respostas += 1
                        if resposta.acertou:
                            total_acertos += 1
                if total_respostas > 0:
                    media = round(total_acertos/total_respostas, 2) *100
                    simulado.media_acertos = media
                    
                else:
                    simulado.media_acertos = 0
                simulado.save()
        
        qs = qs.order_by('-criacao')
        return qs
            
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        classe = self.request.session.get('classe')
        if not classe:
            #redirecionando para login
            return redirect('login')

        if classe == 'Professor':
            pass
        elif classe == 'Coordenador':
            coordenador = Coordenador.objects.get(user=self.request.user)
            escolas = Escola.objects.get(Coordenador=coordenador)
            turmas = escolas.turmas.split(';')
            context['turmas'] = [turma for turma in turmas if turma != '']
            print("turmas: ", turmas)

            

        elif classe == 'Coordenador Geral' or classe == 'Secretário':            
            if CoordenadorGeral.objects.filter(user=self.request.user).exists():
                coordenador_geral = CoordenadorGeral.objects.get(user=self.request.user)
                estado = coordenador_geral.secretario.estado
            else:
                estado = Secretario.objects.get(user=self.request.user).estado
            escolas = Escola.objects.filter(estado=estado)
            context['escolas'] = escolas
        return context
    
    def post(self, *args, **kwargs):
        simulado_id = self.request.POST.get('id') or None
        Simulado.objects.get(id=simulado_id).delete()

        messages.success(self.request, 'Simulado cadastrado com sucesso!')
        return redirect('lista_simulados')
    
class ConstruirSimulado(ListView):
    template_name = 'simulados/simulado_construido.html'
    model = Questao
    login_url = reverse_lazy('login')
    context_object_name = 'questoes'
    paginate_by = 10
    ordering = ['id']
    def get_context_data(self, **kwargs):
        #deletando todas as questoes
        context = super().get_context_data(**kwargs)

        habilidades = HabilidadesBNCC.objects.all()
        context['habilidades'] = habilidades

        #pegando os anos da habilidade
        anos = []
        for habilidade in habilidades:
            ano = habilidade.ano
            if ano not in anos:
                anos.append(ano)

        context['anos'] = anos

        unidades = UnidadeTematica.objects.all()
        context['unidades'] = unidades

        anos_unidades = []
        for unidade in unidades:
            ano = unidade.ano
            if ano not in anos_unidades:
                anos_unidades.append(ano)
        print("Anos: ", anos_unidades)
        context['anos_unidades'] = anos_unidades


        #contando quantas questões tem no queryset
        questoes = self.get_queryset()
        context['qtd_questoes'] = questoes.count()

        

        return context

    def get_queryset(self):
        qs = super().get_queryset()

        unidade = self.request.GET.get('unidade') or None
        if unidade:
            unidade = UnidadeTematica.objects.get(id=unidade)
            qs = qs.filter(unidade__in=[unidade])

        matriz = self.request.GET.get('matriz') or None
        if matriz:
            qs = qs.filter(matriz_referencial=matriz)

        #pegando os campos que começam com "habilidade"
        habilidades = [campo for campo in self.request.GET if campo.startswith('check_')]
        habilidades = [campo.replace('check_', '') for campo in habilidades]
        if habilidades:
            qs = qs.filter(habilidades_abncc__in=habilidades)

        qs = qs.exclude(visivel=False)
        return qs
    
    def post(self, *args, **kwargs):
        nome_simulado = self.request.POST.get('nome_simulado')
        questoes_simulado = self.request.POST.get('questoes_simulado')
        data_limite = self.request.POST.get('data_limite') or None
        info_adicionais = self.request.POST.get('info_adicionais') or ""
        try:
            questoes_simulado = eval(questoes_simulado)
        except:
            questoes_simulado = []

        if data_limite:
            tipo = 'questoes_gerais'
            estado = CoordenadorGeral.objects.get(user=self.request.user).secretario.estado
        else:
            tipo = 'questoes_cadastradas'
            estado = ""

        simulado = Simulado.objects.create(
            nome=nome_simulado, 
            responsavel=self.request.user,
            estado=estado,
            tipo_simulado=tipo,
            data_limite=data_limite,
            info_adicionais=info_adicionais
            )

        for i, questao in enumerate(questoes_simulado):
            QuestaoReferencia.objects.create(
                questao=Questao.objects.get(id=questao),
                simulado=simulado,
                numero_questao=i+1
            )

        #limpando o local storage

        messages.success(self.request, 'Simulado criado com sucesso!')
        return redirect('lista_simulados')

class CadastrarSimulado(SimuladoView, TemplateView):
    template_name = 'simulados/simulado_cadastrado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        unidades = UnidadeTematica.objects.all()
        context['unidades'] = unidades

        #pegando as habilidades
        habilidades = HabilidadesBNCC.objects.all()
        context['habilidades'] = habilidades

        #pegando os anos da habilidade
        anos = []
        for habilidade in habilidades:
            ano = habilidade.ano
            if ano not in anos:
                anos.append(ano)

        context['anos'] = anos
        return context

    def post(self, *args, **kwargs):
        nome_simulado = self.request.POST.get('nome_simulado')

        #criando simulado
        simulado = Simulado.objects.create(
            nome=nome_simulado, 
            responsavel=self.request.user,
            tipo_simulado="questoes_cadastradas"
        )
        
        for i in range(1, 100):
            habilidades = self.request.POST.get(f'habilidades_{i}') or None
            alternativa_correta = self.request.POST.get(f'alternativa_correta_{i}') or None
            if habilidades:
                #criando questao
                questao = Questao.objects.create(
                    habilidades_abncc_texto=habilidades,
                    visivel=False,
                    alternativa_correta= alternativa_correta
                )

                #criando questao referencia
                QuestaoReferencia.objects.create(
                    questao=questao,
                    simulado=simulado,
                    numero_questao=i
                )
            
            

        
        messages.success(self.request, 'Simulado criado com sucesso!')
        return redirect('lista_simulados')

class PreencheGabarito(SimuladoView, DetailView):
    template_name = 'simulados/preenche_gabarito.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'simulado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulado = self.get_object()
        questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
        context['questoes'] = questoes

        professor = Professor.objects.get(user=self.request.user)
        alunos = Aluno.objects.filter(professor=professor).order_by('nome')
        context['alunos'] = alunos

        #pegando as turmas
        turmas = []
        coordenador = professor.coordenador
        escola = Escola.objects.get(Coordenador=coordenador)
        turmas = escola.turmas
        turmas = turmas.split(';')
        turmas = [turma.strip() for turma in turmas]
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
        turma = self.request.POST.get('turma')
        professor = Professor.objects.get(user=self.request.user)
        alunos = Aluno.objects.filter(turma=turma, professor=professor)
        for aluno in alunos: 

            #pegando todos os campos que começam com resposta_
            respostas = [campo for campo in self.request.POST if campo.startswith(f'{aluno.id}_resposta_')]
            respostas = [campo.replace(f'{aluno.id}_resposta_', '') for campo in respostas]
            respostas = [int(resposta) for resposta in respostas]
            #criando respostas para cada questao
            for resposta in respostas:
                questao = QuestaoReferencia.objects.get(id=resposta)

                resposta_correta = questao.questao.alternativa_correta
                acertou = resposta_correta == self.request.POST.get(f'{aluno.id}_resposta_{resposta}')
                valor = self.request.POST.get(f'{aluno.id}_resposta_{resposta}')
                
                #criando resposta
                try:
                    Resposta.objects.create(
                        aluno=aluno,
                        questao_referencia=questao,
                        resposta=valor,
                        acertou=acertou
                    )
                except:
                    pass
        messages.success(self.request, 'Gabarito preenchido com sucesso!')
        return redirect('lista_simulados')

class VisualizarSimulado(DetailView):
    template_name = 'simulados/visualizar_simulado.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'simulado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulado = self.get_object()
        questoes = QuestaoReferencia.objects.filter(simulado=simulado).order_by('numero_questao')
        context['questoes'] = questoes

        
        return context
  
class VisualizarRelatorio(DetailView):
    template_name = 'simulados/visualizar_relatorio.html'
    model = Simulado
    login_url = reverse_lazy('login')
    context_object_name = 'simulado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        simulado = self.get_object()
        filtro = self.request.GET.get('filtro') or None
        valor = self.request.GET.get('valor') or None
        context['filtro'] = filtro
        context['valor'] = valor

        questoes = QuestaoReferencia.objects.filter(simulado=simulado)
        context['questoes'] = questoes


        #agrupando as questoes por quantidade de acertos
        questoes_faceis = []
        questoes_medias = []
        questoes_dificeis = []

        questoes_abaixo_adequado = []
        questoes_basico = []
        questoes_adequado = []
        questoes_avancado = []
        #pegando as respostas de cada questao
        for questao in questoes:
            if filtro == 'turma':
                alunos = Aluno.objects.filter(turma=valor)
                questao.resposta = Resposta.objects.filter(questao_referencia=questao, aluno__in=alunos)
            elif filtro == 'escola':
                alunos = Aluno.objects.filter(escola=valor)
                context['valor'] = Escola.objects.get(id=valor).nome
                questao.resposta = Resposta.objects.filter(questao_referencia=questao, aluno__in=alunos)
            else:
                questao.resposta = Resposta.objects.filter(questao_referencia=questao)
            
            
            #verificando se houve alguma resposta
            if questao.resposta.count() > 0:
                #verificando quantas respostas A teve em porcentagem
                questao.quantidade_respostas_a = round((questao.resposta.filter(resposta='a').count() / questao.resposta.count()) * 100, 2)
                questao.quantidade_respostas_b = round((questao.resposta.filter(resposta='b').count() / questao.resposta.count()) * 100, 2)
                questao.quantidade_respostas_c = round((questao.resposta.filter(resposta='c').count() / questao.resposta.count()) * 100, 2)
                questao.quantidade_respostas_d = round((questao.resposta.filter(resposta='d').count() / questao.resposta.count()) * 100, 2)
                
                
                #verificando quantas respostas corretas teve
                questao.quantidade_respostas_corretas = questao.resposta.filter(acertou=True).count()
            
            
                #calculando a porcentagem de acertos
                questao.porcentagem_acertos = int((questao.quantidade_respostas_corretas / questao.resposta.count()) * 100)
            else:
                questao.porcentagem_acertos = 0
                questao.quantidade_respostas_corretas = 0
                questao.quantidade_respostas_a = 0
                questao.quantidade_respostas_b = 0
                questao.quantidade_respostas_c = 0
                questao.quantidade_respostas_d = 0
        
        
            if questao.porcentagem_acertos >= 80:
                questoes_faceis.append(questao)
            elif questao.porcentagem_acertos >= 55:
                questoes_medias.append(questao)
            else:
                questoes_dificeis.append(questao)

            if questao.porcentagem_acertos <= 35:
                questoes_avancado.append(questao)
            elif questao.porcentagem_acertos <= 60:
                questoes_adequado.append(questao)
            elif questao.porcentagem_acertos <= 75:
                questoes_basico.append(questao)
            else:
                questoes_abaixo_adequado.append(questao)

        context['questoes_faceis'] = questoes_faceis
        context['questoes_medias'] = questoes_medias
        context['questoes_dificeis'] = questoes_dificeis

        context['questoes_regua'] = [questoes_abaixo_adequado, questoes_basico, questoes_adequado, questoes_avancado]
        

        #pegando a taxa de acerto por aluno
        if filtro == 'turma':
            alunos = Aluno.objects.filter(turma=valor)
            respostas = Resposta.objects.filter(questao_referencia__simulado=simulado, aluno__in=alunos)
        elif filtro == 'escola':
            alunos = Aluno.objects.filter(escola=valor)
            respostas = Resposta.objects.filter(questao_referencia__simulado=simulado, aluno__in=alunos)
        else:
            respostas = Resposta.objects.filter(questao_referencia__simulado=simulado)
        alunos = []
        for resposta in respostas:
            if resposta.aluno not in alunos:
                alunos.append(resposta.aluno)
        alunos_abaixo_basico = []
        alunos_basico = []
        alunos_adequado = []
        alunos_avancado = []
        for aluno in alunos:
            aluno.respostas = Resposta.objects.filter(aluno=aluno, questao_referencia__simulado=simulado)
            aluno.quantidade_respostas_corretas = aluno.respostas.filter(acertou=True).count()
            aluno.porcentagem_acertos = int((aluno.quantidade_respostas_corretas / aluno.respostas.count()) * 100)
            aluno.pontuacao = round((aluno.quantidade_respostas_corretas / aluno.respostas.count()) * 10, 2)
            if aluno.porcentagem_acertos >= 80:
                alunos_avancado.append(aluno)
            elif aluno.porcentagem_acertos >= 60:
                alunos_adequado.append(aluno)
            elif aluno.porcentagem_acertos >= 40:
                alunos_basico.append(aluno)
            else:
                alunos_abaixo_basico.append(aluno)
        
        #ordenando alunos pela pontuação
        alunos = sorted(alunos, key=lambda x: x.pontuacao, reverse=True)
        context['alunos'] = alunos

        context['alunos_abaixo_basico'] = alunos_abaixo_basico
        context['alunos_basico'] = alunos_basico
        context['alunos_adequado'] = alunos_adequado
        context['alunos_avancado'] = alunos_avancado

        #pegando qual deles tem o maior len
        maior = 0
        if len(alunos_abaixo_basico) > maior:
            maior = len(alunos_abaixo_basico)
        if len(alunos_basico) > maior:
            maior = len(alunos_basico)
        if len(alunos_adequado) > maior:
            maior = len(alunos_adequado)
        if len(alunos_avancado) > maior:
            maior = len(alunos_avancado)
        
        alunos_regua = []
        for i in range(maior):
            dict_alunos = {}
            try:
                dict_alunos['abaixo_basico'] = alunos_abaixo_basico[i]
            except:
                dict_alunos['abaixo_basico'] = ""

            try:
                dict_alunos['basico'] = alunos_basico[i]
            except:
                dict_alunos['basico'] = ""

            try:
                dict_alunos['adequado'] = alunos_adequado[i]
            except:
                dict_alunos['adequado'] = ""

            try:
                dict_alunos['avancado'] = alunos_avancado[i]
            except:
                dict_alunos['avancado'] = ""

            alunos_regua.append(dict_alunos)
        context['alunos_regua'] = alunos_regua

        return context
    
class SimuladoProficiencia(SimuladoView, TemplateView):
    template_name = 'simulados/simulado_proficiencia.html'
    login_url = reverse_lazy('login')

    def post(self, *args, **kwargs):
        #criando simulado
        simulado = Simulado.objects.create(
            nome= self.request.POST.get('nome_simulado'), 
            responsavel=self.request.user,
            tipo_simulado="questoes_proficiencia"
        )
        simulado.save()

        #pegando os campos que começam com "habilidade"
        habilidades = [campo for campo in self.request.POST if campo.startswith('habilidade_bncc_')]
        numeros = [campo.replace('habilidade_bncc_', '') for campo in habilidades]
        for numero in numeros:
            habilidade = self.request.POST.get(f'habilidade_bncc_{numero}')
            numero_questao_facil = self.request.POST.get(f'numero_questao_facil_{numero}')
            pergunta_facil = self.request.POST.get(f'pergunta_facil_{numero}')
            numero_questao_intermediaria = self.request.POST.get(f'numero_questao_intermediaria_{numero}')
            pergunta_intermediaria = self.request.POST.get(f'pergunta_intermediaria_{numero}')
            numero_questao_dificil = self.request.POST.get(f'numero_questao_dificil_{numero}')
            questao_dificil = self.request.POST.get(f'pergunta_dificil_{numero}')
            

            #criando questao
            questao = QuestaoProficiencia.objects.create(
                simulado=simulado,
                numero_questao_facil=numero_questao_facil,
                questao_facil=pergunta_facil,
                numero_questao_intermediaria=numero_questao_intermediaria,
                questao_intermediaria=pergunta_intermediaria,
                numero_questao_dificil=numero_questao_dificil,
                questao_dificil=questao_dificil,
                habilidade_bncc=habilidade
            )
            questao.save()

        messages.success(self.request, 'Simulado criado com sucesso!')
        return redirect('lista_simulados')
            

