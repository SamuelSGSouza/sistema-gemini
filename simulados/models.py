from django.db import models
from usuarios.models import Professor
from django.contrib.auth.models import User


class UnidadeTematica(models.Model):
    class Meta:
        verbose_name = 'Unidade Temática'
        verbose_name_plural = 'Unidades Temáticas'
    unidade = models.CharField(max_length=255, verbose_name='Unidade Temática')
    ano = models.CharField(max_length=255,verbose_name='Ano', blank=True, null=True)

    def __str__(self):
        return self.unidade

class HabilidadesBNCC(models.Model):
    habilidade = models.CharField(max_length=255, verbose_name='Habilidade da BNCC')
    ano = models.CharField(max_length=255,verbose_name='Ano', blank=True, null=True)

    def __str__(self):
        return self.habilidade

class Simulado(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome do simulado')
    responsavel = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='user', blank=True, null=True)
    tipo_simulado = models.CharField(max_length=255, verbose_name='Tipo do simulado', choices=(
        ("questoes_construidas", "Simulado Construído"),
        ("questoes_cadastradas", "Simulado Cadastrado"),
        ("questoes_proficiencia", "Simulado Proficiência"),
        ("questoes_gerais", "Simulado Geral")
    ), null=True, blank=True)
    estado = models.CharField(max_length=255, verbose_name='Estado', blank=True, null=True)
    data_limite = models.DateField(verbose_name='Data limite', blank=True, null=True)
    info_adicionais = models.TextField(verbose_name='Informações adicionais', blank=True, null=True)
    media_acertos = models.FloatField(verbose_name='Média de acertos', blank=True, null=True)
    criacao = models.DateTimeField(auto_now_add=True, verbose_name='Data de criação')
    


    def __str__(self):
        return self.nome

class QuestaoReferencia(models.Model):
    simulado = models.ForeignKey('simulados.Simulado', on_delete=models.CASCADE, verbose_name='Simulado')
    numero_questao = models.IntegerField(verbose_name='Número da questão')
    questao = models.ForeignKey('simulados.Questao', on_delete=models.CASCADE, verbose_name='Questão')
    quantidade_respostas_a = models.IntegerField(verbose_name='Quantidade de respostas A', blank=True, null=True)
    quantidade_respostas_b = models.IntegerField(verbose_name='Quantidade de respostas B', blank=True, null=True)
    quantidade_respostas_c = models.IntegerField(verbose_name='Quantidade de respostas C', blank=True, null=True)
    quantidade_respostas_d = models.IntegerField(verbose_name='Quantidade de respostas D', blank=True, null=True)
    quantidade_respostas_corretas = models.IntegerField(verbose_name='Quantidade de respostas corretas', blank=True, null=True)

class Questao(models.Model):
    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'

    matriz_referencial = models.CharField(max_length=255, choices=(
        ('matematica', 'Matemática'),
        ('portugues', 'Língua Portuguesa'),
    ),
    default='matematica',
    verbose_name='Matriz Referencial')
    unidade_tematica = models.ManyToManyField('simulados.UnidadeTematica', verbose_name='Unidade Temática', blank=True, default=None)
    habilidades_abncc = models.ManyToManyField(HabilidadesBNCC, verbose_name='Habilidades da BNCC',   blank=True, default=None)
    habilidades_abncc_texto = models.TextField(verbose_name='Objeto do Conhecimento', null=True, blank=True, default=None)
    enunciado = models.TextField(verbose_name='Enunciado', blank=True, null=True)
    alternativa_a = models.TextField( verbose_name='Alternativa A', blank=True, null=True)
    alternativa_a_imagem = models.ImageField(upload_to='alternativa_a_imagem', verbose_name='Alternativa A Imagem', blank=True, null=True)
    alternativa_b = models.TextField( verbose_name='Alternativa B', blank=True, null=True)
    alternativa_b_imagem = models.ImageField(upload_to='alternativa_b_imagem', verbose_name='Alternativa B Imagem', blank=True, null=True)
    alternativa_c = models.TextField( verbose_name='Alternativa C', blank=True, null=True)
    alternativa_c_imagem = models.ImageField(upload_to='alternativa_c_imagem', verbose_name='Alternativa C Imagem', blank=True, null=True)
    alternativa_d = models.TextField( verbose_name='Alternativa D', blank=True, null=True)
    alternativa_d_imagem = models.ImageField(upload_to='alternativa_d_imagem', verbose_name='Alternativa D Imagem', blank=True, null=True)
    alternativa_correta = models.CharField(max_length=255, verbose_name='Resposta',
        choices=(('a', 'A'),
                ('b', 'B'),
                ('c', 'C'),
                ('d', 'D'),)
        )
    suporte_texto = models.TextField(verbose_name='Suporte de Texto', blank=True, null=True)
    suporte_imagem = models.ImageField(upload_to='suporte_imagem', verbose_name='Suporte de Imagem', blank=True, null=True)
    visivel = models.BooleanField(verbose_name='Pergunta Visível Para Todos?', default=True)

    def __str__(self):
        return f"Questão {self.id}"
    
class Resposta(models.Model):
    questao_referencia = models.ForeignKey('simulados.QuestaoReferencia', on_delete=models.CASCADE, verbose_name='Questão de referência')
    resposta = models.CharField(max_length=255, verbose_name='Resposta', choices=(
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
    ))
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, verbose_name='Aluno')
    acertou = models.BooleanField(verbose_name='Acertou?', default=False)
    

    def __str__(self):
        return self.resposta

class QuestaoProficiencia(models.Model):
    simulado = models.ForeignKey('simulados.Simulado', on_delete=models.CASCADE, verbose_name='Simulado')
    numero_questao_facil = models.IntegerField(verbose_name='Número da questão fácil')
    questao_facil = models.TextField(verbose_name='Questão fácil')
    numero_questao_intermediaria = models.IntegerField(verbose_name='Número da questão médio')
    questao_intermediaria = models.TextField(verbose_name='Questão médio')
    numero_questao_dificil = models.IntegerField(verbose_name='Número da questão difícil')
    questao_dificil = models.TextField(verbose_name='Questão difícil')
    habilidade_bncc = models.CharField(max_length=255, verbose_name='Habilidade da BNCC')

    def __str__(self):
        return f"Questão de Proficiência do Simulado {self.simulado}"
    
class RespostaProficiencia(models.Model):
    questao_proficiencia = models.ForeignKey('simulados.QuestaoProficiencia', on_delete=models.CASCADE, verbose_name='Questão de Proficiência')
    questao_facil_acertou = models.BooleanField(verbose_name='Acertou a questão fácil?', default=False)
    questao_medio_acertou = models.BooleanField(verbose_name='Acertou a questão médio?', default=False)
    questao_dificil_acertou = models.BooleanField(verbose_name='Acertou a questão difícil?', default=False)
    pontuacao = models.FloatField(verbose_name='Pontuação', blank=True, null=True)
    aluno = models.ForeignKey('usuarios.Aluno', on_delete=models.CASCADE, verbose_name='Aluno')

    def __str__(self):
        return f"Resultado do Aluno {self.aluno}"
