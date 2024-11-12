from django import forms
from .models import Configuracao

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_aplicacao', 'cliente_padrao', 'cor_primaria', 'cor_secundaria', 'logo_empresa']
        widgets = {
            'cor_primaria': forms.TextInput(attrs={'type': 'color'}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color'}),
        }
