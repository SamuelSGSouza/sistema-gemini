from django.contrib import admin
from .models import *

@admin.register(UnidadeTematica)
class UnidadeTematicaAdmin(admin.ModelAdmin):
    list_display = ("unidade", )

@admin.register(HabilidadesBNCC)
class HabilidadesBNCCAdmin(admin.ModelAdmin):
    list_display = ("habilidade", )

@admin.register(Simulado)
class SimuladoAdmin(admin.ModelAdmin):
    list_display = ("nome", )
    list_filter = ("nome", )

@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ("habilidades_abncc_texto",   )
    list_filter = ("habilidades_abncc_texto",  )
    search_fields = ("unidade_tematica", "habilidades_abncc", "nivel_proficiencia", )

@admin.register(Resposta)
class RespostaAdmin(admin.ModelAdmin):
    list_display = ("resposta",)
    list_filter = ("resposta",)

@admin.register(ComponenteCurricular)
class ComponenteCurricularAdmin(admin.ModelAdmin):
    list_display = ("componente",)
    list_filter = ("componente",)

@admin.register(Descritor)
class DescritorAdmin(admin.ModelAdmin):
    list_display = ("descritor",)
    list_filter = ("descritor",)