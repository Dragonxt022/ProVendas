# estoque/forms.py
from django import forms
from .models import CategoriaProduto, Produto

class CategoriaProdutoForm(forms.ModelForm):
    class Meta:
        model = CategoriaProduto
        fields = ['nome', 'file']  # Inclua todos os campos do seu formulário aqui

    def __init__(self, *args, **kwargs):
        super(CategoriaProdutoForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['codigo_barras', 'nome', 'descricao', 'preco_de_venda', 'preco_de_cursto', 'quantidade_estoque', 'categoria', 'file', 'status']  # Inclua todos os campos necessários
        
        widgets = {
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de barras'}),
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do Produto'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição do Produto', 'rows': 3}),
            'preco_de_venda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço de venda', 'step': '0.01'}),
            'preco_de_cursto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preço de custo', 'step': '0.01'}),
            'quantidade_estoque': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade em Estoque'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
            