from django import forms
from .models import *

class ProfessorForm(forms.ModelForm):
    class Meta:
        model = Professor
        fields = '__all__'
