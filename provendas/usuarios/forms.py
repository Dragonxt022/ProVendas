from django import forms
from django.contrib.auth.models import User, Group
from .models import Perfil  # Importa o modelo Perfil

class UsuarioForm(forms.ModelForm):
    # Campos de senha com ícones
    nova_senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nova Senha'}),
        label='Nova Senha'
    )
    confirmar_senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Senha'}),
        label='Confirmar Senha'
    )

    grupos = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'multiple': 'multiple'}),
        required=True
    )
    foto_perfil = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )
    

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'grupos', 'foto_perfil']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sobrenome'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')

        # Verifica se ambas as senhas foram fornecidas e se correspondem
        if nova_senha or confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError("As senhas não correspondem. Por favor, verifique.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        nova_senha = self.cleaned_data.get('nova_senha')

        # Se uma nova senha for fornecida, altere a senha do usuário
        if nova_senha:
            user.set_password(nova_senha)

        if commit:
            user.save()
            self.save_m2m()  # Salva as relações many-to-many, como os grupos

        return user
