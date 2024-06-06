from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from simulados import models as simulados_models

ESTADOS = (
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espirito Santo'),
        ('GO', 'Goiás'),
        ('MA', 'Maranhão'),
        ('MS', 'Mato Grosso do Sul'),
        ('MT', 'Mato Grosso'),
        ('MG', 'Minas Gerais'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PR', 'Paraná'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('RN', 'Rio Grande do Norte'),
        ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'),
        ('RR', 'Roraima'),
        ('SC', 'Santa Catarina'),
        ('SP', 'São Paulo'),
        ('SE', 'Sergipe'),
        ('TO', 'Tocantins'),
    )


class Secretario(models.Model):
    nome_completo = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, verbose_name='CPF (somente números)', blank=True, null=True)
    telefone = models.CharField(max_length=17, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    endereco = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, choices=ESTADOS)
    rede = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = 'Secretário'
        verbose_name_plural = 'Secretários'
@receiver(post_delete, sender=Secretario)
def delete_coord(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()

class CoordenadorGeral(models.Model):
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name='CPF (somente números)')
    telefone = models.CharField(max_length=17, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    secretario = models.ForeignKey(Secretario, on_delete=models.CASCADE, blank=True, null=True) 

    def __str__(self):
        return self.nome_completo
    
    class Meta:
        verbose_name = 'Coordenador Geral'
        verbose_name_plural = 'Coordenadores Gerais'

@receiver(post_delete, sender=CoordenadorGeral)
def delete_coord_ge(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()


#cordenadores
class Coordenador(models.Model):
    #definindo o plural name
    class Meta:
        verbose_name = 'Coordenador de Escola'
        verbose_name_plural = 'Coordenadores de Escola'

    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, verbose_name='CPF (somente números)', null=True, blank=True)
    telefone = models.CharField(max_length=17, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    coordenador_geral = models.ForeignKey(CoordenadorGeral, on_delete=models.CASCADE, blank=True, null=True)
    escola = models.ForeignKey('Escola', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.nome_completo
    
@receiver(post_delete, sender=Coordenador)
def delete_coord(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
    
class Escola(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=100, choices=(ESTADOS))
    municipio = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.nome

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    grau = models.CharField(max_length=100, choices=(
        ('1', '1º ano'), 
        ('2', '2º ano'),
        ('3', '3º ano'), 
        ('4', '4º ano'), 
        ('5', '5º ano'),
        ('6', '6º ano'), 
        ('7', '7º ano'), 
        ('8', '8º ano'), 
        ('9', '9º ano'),
        ('10', '1º ano do ensino médio'),
        ('11', '2º ano do ensino médio'),
        ('12', '3º ano do ensino médio')
    ), default='1')
    escola = models.ForeignKey(Escola, on_delete=models.CASCADE)
    simulados_respondidos = models.ManyToManyField(simulados_models.Simulado, blank=True)
    
    def __str__(self):
        return "Turma: " + self.nome + " - Escola: " + self.escola.nome

#professores
class Professor(models.Model):
    class Meta:
        verbose_name_plural = 'Professores'
    nome_completo = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, verbose_name='CPF (somente números)', blank=True, null=True)
    telefone = models.CharField(max_length=17, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    coordenador = models.ForeignKey(Coordenador, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome_completo


@receiver(post_delete, sender=Professor)
def delete_prof(sender, instance, **kwargs):
    if instance.user:
        instance.user.delete()
    
#alunos
class Aluno(models.Model):
    nome = models.CharField(max_length=100)
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, blank=True, null=True)


    def __str__(self):
        return self.nome


    
