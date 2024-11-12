from django import forms
from .models import Configuracao

class ConfiguracaoForm(forms.ModelForm):
    class Meta:
        model = Configuracao
        fields = ['nome_aplicacao', 'cor_principal', 'cliente_padrao']
