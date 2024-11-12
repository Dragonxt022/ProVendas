from django import forms
from .models import Configuracao

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_aplicacao', 'cliente_padrao', 'cor_primaria', 'cor_secundaria', 'logo_empresa', 'icone_aplicacao']
        widgets = {
            'nome_aplicacao': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente_padrao': forms.Select(attrs={'class': 'form-control'}),
            'cor_primaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'logo_empresa': forms.FileInput(attrs={'class': 'form-control'}),
            'icone_aplicacao': forms.FileInput(attrs={'class': 'form-control'}),
        }
