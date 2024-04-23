from django.contrib import admin
from .models import *

@admin.register(Secretario)
class SecretarioAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', )
    search_fields = ('nome_completo', 'email', )

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turma', )
    search_fields = ('nome', 'turma',)

    def turma(self, obj):
        return obj.turma.nome
    
    turma.short_description = 'Turma'

class AlunoInline(admin.TabularInline):
    model = Aluno
    extra = 0

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    inlines = [AlunoInline]
    list_display = ['nome', 'escola_nome']
    search_fields = ['nome', 'escola__nome']

    def escola_nome(self, obj):
        return obj.escola.nome

    escola_nome.short_description = 'Escola'

class TurmaInline(admin.TabularInline):
    model = Turma
    extra = 0
@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    inlines = [TurmaInline]
    list_display = ('nome', 'estado', "municipio" )
    search_fields = ('nome', 'estado', "municipio" )

@admin.register(Coordenador)
class CoordenadorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email', 'user', )
    search_fields = ('nome_completo', 'email', 'user', )

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('nome_completo', 'email',  'coordenador')
    search_fields = ('nome_completo', 'email', 'coordenador')
    

    