# usuarios/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from .models import Perfil  # Importa o modelo Perfil

class UsuarioForm(forms.ModelForm):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'}),
        required=True
    )
    foto_perfil = forms.ImageField(required=False)  # Campo para upload de imagem

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'grupos', 'foto_perfil']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
