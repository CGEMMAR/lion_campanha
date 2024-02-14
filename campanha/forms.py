from django import forms

from campanha.utils import CPFValidator, ChaveValidator
from .models import Participante

class EntrarParticipanteForm(forms.Form):
    chave = forms.CharField(max_length=8, help_text='Esta é sua chave única para criar uma conta, não mude.', validators=[ChaveValidator()])
    cpf = forms.CharField(max_length=14, min_length=14, validators=[CPFValidator()],)

    def clean(self):
        cleaned_data = super(EntrarParticipanteForm, self).clean()

        if(cleaned_data.get("cpf")):
            cleaned_data["cpf"] = "".join(char for char in cleaned_data["cpf"] if char.isdigit())

        return self.cleaned_data
    class Meta:
        help_texts = {
            'chave': 'Esta é sua chave única para criar uma conta, não mude.',
        }

class CadastroParticipanteForm(forms.ModelForm):
    telefone = forms.CharField(max_length=15, min_length=15)

    class Meta:
        model = Participante
        fields = ['nome', 'nome_responsavel', 'nascimento', 'telefone', 'obs', 'confirmado', 'tem_receita', 'quem_indicou']
        widgets = {
            'nascimento': forms.DateInput(attrs={'type': 'date'})
        }

    def clean(self):
        cleaned_data = super(CadastroParticipanteForm, self).clean()

        if(cleaned_data.get("telefone")):
            cleaned_data["telefone"] = "".join(char for char in cleaned_data["telefone"] if char.isdigit())

        return self.cleaned_data
        