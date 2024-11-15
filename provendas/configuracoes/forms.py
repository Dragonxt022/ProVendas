from django import forms
from .models import Configuracao
from clientes.models import Cliente  # Importando o modelo de Cliente

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_aplicacao', 'cliente_padrao', 'cor_primaria', 'cor_secundaria', 'logo_empresa', 'icone_aplicacao']
        widgets = {
            'cliente_padrao': forms.Select(attrs={'class': 'form-control'}),  # Aplicando a classe CSS
            'cor_primaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'nome_aplicacao': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_empresa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'icone_aplicacao': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
