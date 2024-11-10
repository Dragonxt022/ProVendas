from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nome', 'email', 'cpf', 'telefone', 'data_nascimento', 
            'endereco', 'cidade', 'estado', 'cep', 'status'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'id': 'nome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control', 'id': 'cpf'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'id': 'telefone'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'data_nascimento'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'id': 'endereco'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'id': 'cidade'}),
            'estado': forms.Select(attrs={'class': 'form-control', 'id': 'estado'}, choices=[
                ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), 
                ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), 
                ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), 
                ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), 
                ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), 
                ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), 
                ('SE', 'Sergipe'), ('TO', 'Tocantins')
            ]),
            'cep': forms.TextInput(attrs={'class': 'form-control', 'id': 'cep'}),
            'status': forms.Select(attrs={'class': 'form-control', 'id': 'status'}),
        }