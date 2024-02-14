from django.forms import ValidationError
from django.utils.deconstruct import deconstructible
from .models import Chave

def validar_cpf(numbers):
    #  Obtém os números do CPF e ignora outros caracteres
    cpf = [int(char) for char in numbers if char.isdigit()]

    #  Verifica se o CPF tem 11 dígitos
    if len(cpf) != 11:
        return False

    #  Verifica se o CPF tem todos os números iguais, ex: 111.111.111-11
    #  Esses CPFs são considerados inválidos mas passam na validação dos dígitos
    #  Antigo código para referência: if all(cpf[i] == cpf[i+1] for i in range (0, len(cpf)-1))
    if cpf == cpf[::-1]:
        return False

    #  Valida os dois dígitos verificadores
    for i in range(9, 11):
        value = sum((cpf[num] * ((i+1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != cpf[i]:
            return False
    return True

class CPFValidator:
    code = "invalid"
    message = "CPF inválido."

    def __call__(self, value):
        if(not validar_cpf(value)):
            raise ValidationError(self.message, code=self.code, params={"value": value})
        
class ChaveValidator:
    code = "invalid"
    message = "Chave não reconhecida, verifique se inseriu a chave corretamente, se sim, contate o provedor."

    def __call__(self, value):
        # chave = Chave.objects.get(chave="123")
        try:
            chave = Chave.objects.get(chave=value)
        except Chave.DoesNotExist:
            chave = None

        if(not chave):
            # Chave não encontrada
            raise ValidationError(self.message, code=self.code, params={"value": value})

        if(chave.participante):
            # A chave já foi usada
            raise ValidationError(self.message, code=self.code, params={"value": value})
