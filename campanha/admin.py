import asyncio
from http.client import METHOD_NOT_ALLOWED
import secrets
import string
from urllib.parse import urlencode
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from .models import Campanha, Medico, Participante, Chave
from django.utils.translation import ngettext
from django.conf import settings

# Register your models here.


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ("data_hora_inicio", "data_hora_final", "ver_chaves_link")
    actions = ["gerar_chaves"]
    list_display_links = ("data_hora_inicio", "data_hora_final")

    def ver_chaves_link(self, obj):
        count = obj.chave_set.count()

        url = (
            reverse("admin:campanha_chave_changelist")
            + "?"
            + urlencode({"campanha__id__exact": f"{obj.id}"})
        )
        return format_html(f'<a href="{url}">{count} Chaves</a>')

    ver_chaves_link.short_description = "Chaves"
    
    @admin.action(description="Gerar chaves", permissions=["generate"])
    def gerar_chaves(self, request, queryset):
        print("gerar_chaves")

        def gerar_chaves_aleatorias(campanha_id):
            # Gera uma string de 4 digitos com letras maiúsculas e números
            return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4)) + str(campanha_id)

        def gerar_chaves_unicas(campanha_id, num_chaves):
            keys = set()
            while len(keys) < num_chaves:
                keys.add(gerar_chaves_aleatorias(campanha_id))
            return keys

        print(queryset.all())

        campanha_not_generated = []
        campanha_generated = []
        chavesObj = []
        for campanha in queryset.all():
            if(campanha.chave_set.first()):
                campanha_not_generated.append(campanha.id)
            else:
                campanha_generated.append(campanha.id)
                chaves = gerar_chaves_unicas(campanha.id, campanha.qtd_participantes)
                for chave in chaves:
                    chavesObj.append(Chave(chave = chave, campanha = campanha))
                print("chaves")
                print(chaves)
    
        Chave.objects.bulk_create(chavesObj)

        if(campanha_generated and campanha_not_generated):
            self.message_user(
                request,
                f"Chaves geradas para {len(campanha_generated)} campanha{"s" if len(campanha_generated) > 1 else ""}, porém ja existentes para outra{"s" if len(campanha_not_generated) > 1 else ""} {len(campanha_not_generated)} campanha{"s" if len(campanha_not_generated) > 1 else ""}",
                messages.SUCCESS,
            )
        elif(campanha_generated):
            self.message_user(
                request,
                f"Chaves geradas para {len(campanha_generated)} campanha{"s" if len(campanha_generated) > 1 else ""}",
                messages.SUCCESS,
            )
        elif(campanha_not_generated):
            self.message_user(
                request,
                f"As chaves já existem para {f"essas {len(campanha_not_generated)}" if len(campanha_not_generated) > 1 else "essa"} campanha{"s" if len(campanha_not_generated) > 1 else ""}",
                messages.ERROR,
            )

    def has_generate_permission(self, request):
        return request.user.has_perm(f"{self.opts.app_label}.generate_chave")

@admin.register(Medico)
class MedicoAdmin(admin.ModelAdmin):
    pass

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    pass

@admin.register(Chave)
class ChaveAdmin(admin.ModelAdmin):
    list_display = ("chave", "campanha", "copiar_link")
    list_filter = ("campanha",)

    def copiar_link(self, obj):
        if obj.participante:
            return f'Participante "{obj.participante.nome}" usou esta chave'
        else:
            return format_html(f'<button type="button" class="button" onclick="navigator.clipboard.writeText(window.location.origin + \'{reverse("home")}?chave={obj.chave}\')">Copiar URL</button>')

    copiar_link.short_description = "Para participante"
