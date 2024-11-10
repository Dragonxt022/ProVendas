# comanda/forms.py

from django import forms
from .models import Mesa

class MesaForm(forms.ModelForm):
    class Meta:
        model = Mesa
        fields = ['nome', 'status']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',  # Classe do Bootstrap para estilização
                'id': 'nome',
                'placeholder': 'Digite o nome ou número da mesa'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',  # Classe do Bootstrap para estilização
                'id': 'status',
            }),
        }
