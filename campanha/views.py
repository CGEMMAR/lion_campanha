from urllib.parse import urlencode
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import CadastroParticipanteForm, EntrarParticipanteForm
from django.views.decorators.http import require_http_methods
from django.contrib.sessions.models import Session
from .models import Chave, Participante

def _ja_cadastrado(nome):
    return redirect(f'{reverse('conclusao')}{"?" + urlencode({ 'tipo': 1, 'nome': nome})}')

def _outro_cadastro(nome):
    return redirect(f'{reverse('conclusao')}{"?" + urlencode({ 'tipo': 2, 'nome': nome })}') 

def _primeiro_cadastro(nome):
    return redirect(f'{reverse('conclusao')}{"?" + urlencode({ 'tipo': 0, 'nome': nome })}') 

def home(request):
    if(request.method == "POST"):
        form = EntrarParticipanteForm(request.POST)
        
        if form.is_valid():

            #verificar se user já existe, se sim cadastro na campanha completo.
            try:
                participante = Participante.objects.get(cpf=form.cleaned_data["cpf"])
                #participante já existe
                chave = Chave.objects.get(chave=form.cleaned_data["chave"])
    
                participante_chaves = Chave.objects.filter(participante=participante)
                if(participante_chaves):
                    campanhas_participante_id = list(map(lambda c: c.campanha_id, participante_chaves))
                    if(chave.campanha_id in campanhas_participante_id):
                        return _ja_cadastrado(participante.nome)
                chave.participante = participante
                chave.save()
                return _outro_cadastro(participante.nome)
            except Participante.DoesNotExist:
                pass

            request.session["chave"] = form.cleaned_data["chave"]
            request.session["cpf"] = form.cleaned_data["cpf"]
            return redirect("cadastro")
        else:
            return render(request, "participante/home.html", {"form": form})
        
    else: 
        chaveUrl = request.GET.get("chave", "")
        initial = {'chave': chaveUrl}
        if(chaveUrl == ""):
            chaveSession = request.session.get("chave")
            if(chaveSession):
                initial["chave"] = chaveSession
        cpf = request.session.get("cpf")
        if(cpf):
            initial["cpf"] = cpf
        form_chave = EntrarParticipanteForm(initial=initial)
        return render(request, "participante/home.html", {"form": form_chave})

def cadastro(request):
    if(request.method == "POST"):
        form_cadastro = CadastroParticipanteForm(request.POST)

        if form_cadastro.is_valid():
            chave_value = request.session["chave"]
            cpf = request.session["cpf"]

            try:
                chave = Chave.objects.get(chave=chave_value)
                if(chave.participante):
                    raise Chave.DoesNotExist
                participante = Participante(**form_cadastro.cleaned_data, cpf=cpf,)
                participante.save()
                chave.participante = participante
                chave.save()
            except Chave.DoesNotExist:
                return redirect(f'{reverse('home')}{"?" + urlencode({ 'chave': chave_value }) if chave_value else ''}')
            
            # Cadastro bem sucedido
            request.session.pop("chave")
            request.session.pop("cpf")
            if(not request.session.keys()):
                #se session está vazio, então excluir
                request.session.flush()

            return _primeiro_cadastro(participante.nome)
        else:
            return render(request, "participante/cadastro.html", {"form": form_cadastro})
        
    else:
        chave = request.session.get("chave")
        if(chave and request.session.get("cpf")):
            return render(request, "participante/cadastro.html", {"form": CadastroParticipanteForm})
        else:
            return redirect(f'{reverse('home')}{"?" + urlencode({ 'chave': chave }) if chave else ''}')

def conclusao(request):
    tipo = request.GET.get("tipo")
    nome = request.GET.get("nome", "")

    # 1 - Já cadastrado
    # 2 - Cadastrado Novamente
    # primeiro cadastro

    return render(request, "participante/conclusao.html", {"tipo": tipo, "nome": nome})