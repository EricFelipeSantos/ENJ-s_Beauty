#1. criar a pasta templatetags dentro do app
#2. criar o arquivo custom_filters.py dentro da pasta templatetags
#3. criar o arquivo __init__.py dentro da pasta templatetags
#4. adicionar o codigo abaixo no arquivo custom_filters.py
#5. rodar no terminal o seguinte:
#       python manage.py shell
#       from cadastros.templatetags import custom_filters

from django import template

register = template.Library()

#filtros do cadastro de usuarios
@register.filter
def tem_perfil(usuario, perfil_nome):
    return usuario.perfis.filter(nome=perfil_nome).exists()

#-----------------------------------
