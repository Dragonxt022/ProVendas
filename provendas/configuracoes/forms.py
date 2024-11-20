from django import forms
from .models import Configuracao
from clientes.models import Cliente  # Importando o modelo de Cliente

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = [
            'nome_aplicacao',
            'cliente_padrao',
            'cor_primaria',
            'cor_secundaria',
            'logo_empresa',
            'icone_aplicacao',
            'gerar_codigo_barra_automatico',  # Novo campo
            'gerenciar_abertura_fechamento_caixa',  # Novo campo
        ]
        widgets = {
            'cliente_padrao': forms.Select(attrs={'class': 'form-control'}),
            'cor_primaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'cor_secundaria': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'nome_aplicacao': forms.TextInput(attrs={'class': 'form-control'}),
            'logo_empresa': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'icone_aplicacao': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'gerar_codigo_barra_automatico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Checkbox para geração automática
            'gerenciar_abertura_fechamento_caixa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Checkbox para gerenciamento de caixa
        }