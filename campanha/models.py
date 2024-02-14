from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.html import format_html

# Create your models here.

class Medico(models.Model):
    nome = models.CharField(max_length=60)
    especialidade = models.CharField(max_length=60)

    def __str__(self):
        return self.nome

class Campanha(models.Model):
    descricao = models.CharField(max_length=60)
    data_hora_inicio = models.DateTimeField()
    data_hora_final = models.DateTimeField()
    local = models.CharField(max_length=60)
    qtd_participantes = models.IntegerField()
    data_entrega = models.DateField()
    local_entrega_oculos = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    medicos = models.ManyToManyField(Medico, verbose_name="medicos responsáveis")

    def __str__(self):
        # print(dir(self.chave_set))
        return f'de "{self.data_hora_inicio.strftime("%d/%m/%Y %H:%M:%S")}" até "{self.data_hora_final.strftime("%d/%m/%Y %H:%M:%S")}".'

class Participante(models.Model):
    nome = models.CharField(max_length=60)
    nome_responsavel = models.CharField(max_length=60)
    nascimento = models.DateField()
    telefone = models.CharField(max_length=11)
    obs = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    confirmado = models.BooleanField()
    tem_receita = models.BooleanField()
    quem_indicou = models.CharField(max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # chaves = models.ManyToManyField(Chave, verbose_name="lista de chaves")

    def __str__(self):
        return self.nome

class Chave(models.Model):
    chave = models.CharField(max_length=60)
    campanha = models.ForeignKey(Campanha, on_delete=models.CASCADE, verbose_name="a campanha relacionada")
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE, verbose_name="O participante relacionado", blank=True, null=True)

    def __str__(self):
        return self.chave
    
    class Meta:
        permissions = [
            (
                "generate_chave",
                "Can generate chave"
            )
        ]

