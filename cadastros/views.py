from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, F, Count, Subquery, OuterRef, FloatField, Sum, ExpressionWrapper
from .models import Usuario, Perfil, Servico, Horario
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from datetime import datetime

#Cadastro usuários
@login_required
def usuarios(request):
    if request.session.get('perfil_atual') not in {'Proprietário'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')

    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_usuario":
            email = request.POST.get('txtEmail')
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já está em uso!')
                return redirect('cadastros:usuarios')

            usuario = Usuario(
                nome=request.POST.get('txtNome'),
                email=email,
                telefone=request.POST.get('txtTelefone')
            )
            usuario.set_password(request.POST.get('txtSenha'))
            usuario.save()
            
            perfis = request.POST.getlist('chkPerfis')
            for perfil_id in perfis:
                perfil = Perfil.objects.get(id=perfil_id)
                usuario.perfis.add(perfil)
                
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('cadastros:usuarios')

        elif acao == "alterar_usuario":
            usuario_id = request.POST.get('txtId')
            usuario = Usuario.objects.get(id=usuario_id)
            usuario.nome = request.POST.get('txtNome')
            usuario.email = request.POST.get('txtEmail')
            usuario.telefone = request.POST.get('txtTelefone')
            if request.POST.get('txtSenha'):
                usuario.set_password(request.POST.get('txtSenha'))
            usuario.save()
            
            usuario.perfis.clear()
            perfis = request.POST.getlist('chkPerfis')
            for perfil_id in perfis:
                perfil = Perfil.objects.get(id=perfil_id)
                usuario.perfis.add(perfil)

            messages.success(request, 'Usuário atualizado com sucesso!')
            return redirect('cadastros:usuarios')

    usuarios_lista = Usuario.objects.all().order_by('nome').exclude(Q(id=request.session['id_atual']))
    paginator = Paginator(usuarios_lista, settings.NUMBER_GRID_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    perfis_lista = Perfil.objects.all()

    return render(request, "usuarios.html", {
        'page_obj': page_obj,
        'perfis': perfis_lista,
    })

@login_required
def verificar_email(request):
    email = request.GET.get('email', None)
    data = {
        'is_taken': Usuario.objects.filter(email=email).exists()
    }
    return JsonResponse(data)

@login_required
def obter_usuario_por_id(request):
    usuario_id = request.GET.get('usuario_id', None)
    usuario = Usuario.objects.get(id=usuario_id)
    perfis_usuario = usuario.perfis.values_list('id', flat=True)
    usuario_dados = {
        'id': usuario.id,
        'nome': usuario.nome,
        'email': usuario.email,
        'senha': '',
        'telefone': usuario.telefone,
        'perfis': list(perfis_usuario),
    }
    return JsonResponse(usuario_dados)

@login_required
def excluir_usuario(request):
    if request.method == "POST":
        usuario_id = request.POST.get('usuario_id')
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
        return JsonResponse({'success': True})

@login_required
def pesquisar_usuario_por_nome(request):
    query = request.GET.get('usuario_nome', '')
    page_number = request.GET.get('page')

    usuarios_lista = Usuario.objects.filter(nome__icontains=query).order_by('nome').exclude(Q(id=request.session['id_atual']))

    paginator = Paginator(usuarios_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(page_number)

    return JsonResponse({
        'html': render_to_string('usuarios_table.html', {'page_obj': page_obj, 'query': query, 'request': request})
    })

#--------------------------------------------------------------------------------------------------------------------
#Cadastro serviços

@login_required
def servicos(request):
    if request.session.get('perfil_atual') not in {'Proprietário'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_servico":
            nome = request.POST.get('txtNome')
            valor = request.POST.get('numValor')
            
            servico = Servico(
                nome=nome,
                valor=valor,
            )
            
            servico.save()

            messages.success(request, 'Serviço cadastrado com sucesso!')
            return redirect('cadastros:servicos')

        elif acao == "alterar_servico":
            servico_id = request.POST.get('txtId')
            servico = Servico.objects.get(id=servico_id)

            servico.nome = request.POST.get('txtNome')
            servico.valor = request.POST.get('numValor')
            servico.save()

            messages.success(request, 'Serviço atualizado com sucesso!')
            return redirect('cadastros:servicos')

    servicos_lista = Servico.objects.all().order_by('nome')

    paginator = Paginator(servicos_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "servicos.html", {'page_obj': page_obj})

@login_required
def obter_servico_por_id(request):
    servico_id = request.GET.get('servico_id', None)
    servico = Servico.objects.get(id=servico_id)
    
    #responsaveis
    responsaveis = servico.responsaveis.values('id', 'nome', 'email', 'telefone').order_by('nome')
    
    servico_dados = {
        'id': servico.id,
        'nome': servico.nome,
        'valor': servico.valor,
        'responsaveis': list(responsaveis),
    }

    return JsonResponse(servico_dados)

@login_required
def excluir_servico(request):
    if request.method == "POST":
        servico_id = request.POST.get('servico_id')
        servico = Servico.objects.filter(id=servico_id).first()
        servico.delete()
        
        return JsonResponse({'success': True, 'message': 'Serviço excluído com sucesso!'})
    return JsonResponse({'success': False, 'message': 'Você não tem permissão para acesso.'}, status=405)
    
@login_required
def pesquisar_servico_por_nome(request):
    servico_nome = request.GET.get('servico_nome', '')
    numero_pagina = request.GET.get('page')
    
    servicos_lista = Servico.objects.filter(nome__icontains=servico_nome).order_by('nome')

    paginator = Paginator(servicos_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(numero_pagina)

    return JsonResponse({
        'html': render_to_string('servicos_table.html', {'page_obj': page_obj, 'query': servico_nome, 'request': request})
    })

#RELACIONANDO ATIVIDADES COM RESPONSAVEIS (USUARIOS)
@login_required
def adicionar_responsavel_de_servico(request):
    servico_id = request.POST.get('servico_id')
    responsavel_id = request.POST.get('responsavel_id')

    servico = Servico.objects.get(id=servico_id)
    responsavel = Usuario.objects.get(id=responsavel_id)
    servico.responsaveis.add(responsavel)
    
    return JsonResponse({'success': True, 'message': 'Responsavel adicionado com sucesso!'})
    
@login_required
def excluir_responsavel_de_servico(request):
    servico_id = request.POST.get('servico_id')
    responsavel_id = request.POST.get('responsavel_id')

    servico = Servico.objects.get(id=servico_id)
    responsavel = Usuario.objects.get(id=responsavel_id)
    servico.responsaveis.remove(responsavel)
    
    return JsonResponse({'success': True, 'message': 'Responsavel removido com sucesso!'})

@require_POST    
@login_required
def exibir_responsaveis_possiveis_para_servico(request):
    servico_id = request.POST.get('txtPostIdResponsaveis')    
    responsaveis = Usuario.objects.order_by('nome').exclude(nome__iexact="Cliente")

    responsaveis_ja_associados = []
    if servico_id:
        servico = Servico.objects.get(id=servico_id)
        responsaveis_ja_associados = list(servico.responsaveis.values_list('id', flat=True))

    paginator = Paginator(responsaveis, settings.NUMBER_GRID_MODAL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'servico_id': servico_id,
        'responsaveis_ja_associados': responsaveis_ja_associados
    }
    
    #carrega a pagina de adicao de responsaveis a atividades
    return render(request, 'servicos_add_responsaveis.html', context)

@login_required
def pesquisar_responsavel_por_nome_para_servico(request):
    nome = request.GET.get('nome', '')
    page_number = request.GET.get('page', 1)
    servico_id = request.GET.get('servico_id', '')
    responsaveis = Usuario.objects.filter(nome__icontains=nome).order_by('nome')

    responsaveis_ja_associados = []
    if servico_id:
        servico = Servico.objects.get(id=servico_id)
        responsaveis_ja_associados = list(servico.responsaveis.values_list('id', flat=True))

    paginator = Paginator(responsaveis, settings.NUMBER_GRID_MODAL)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'servico_id': servico_id,
        'responsaveis_ja_associados': responsaveis_ja_associados,
        'request': request
    }
    
    #carrega o grid com responsaveis atualizado dentro de atividades_add_responsaveis.html
    html = render_to_string('servico_add_responsaveis_table.html', context)
    return JsonResponse({'html': html})
#--------------------------------------------------------------------------------------------------------------------
#Cadastro horários

@login_required
def horarios(request):
    if request.session.get('perfil_atual') not in {'Proprietário', 'Funcionário'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":
        acao = request.POST.get("btnAcao")

        if acao == "novo_horario":
            data = request.POST.get('dateData')
            hora = request.POST.get('timeHorario')
            
            horario = Horario(
                data=data,
                hora=hora,
            )
            
            horario.save()

            messages.success(request, 'Horário cadastrado com sucesso!')
            return redirect('cadastros:horarios')

        elif acao == "alterar_horario":
            horario_id = request.POST.get('txtId')
            horario = Horario.objects.get(id=horario_id)

            horario.data = request.POST.get('dateData')
            horario.hora = request.POST.get('timeHorario')
            horario.save()

            messages.success(request, 'Horario atualizado com sucesso!')
            return redirect('cadastros:horarios')

    horarios_lista = Horario.objects.all().order_by('data')

    paginator = Paginator(horarios_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "horarios.html", {'page_obj': page_obj})

@login_required
def obter_horario_por_id(request):
    horario_id = request.GET.get('horario_id', None)
    horario = Horario.objects.get(id=horario_id)
    
    #servicos = horario.servicos.values('id', 'nome', 'valor', 'responsaveis').distinct().order_by('nome')
    
    servicos = horario.servicos.prefetch_related('responsaveis').distinct().order_by('nome')
    
    servicos_list = []
    for servico in servicos:
        servicos_list.append({
            'id': servico.id,
            'nome': servico.nome,
            'valor': servico.valor,
            'responsaveis': [r.nome for r in servico.responsaveis.all()]  # Ajuste conforme necessário
        })

    horario_dados = {
        'id': horario.id,
        'data': horario.data,
        'hora': horario.hora,
        'servicos': servicos_list,
    }

    return JsonResponse(horario_dados)

@login_required
def excluir_horario(request):
    if request.method == "POST":
        horario_id = request.POST.get('horario_id')
        horario = Horario.objects.filter(id=horario_id).first()
        horario.delete()
        
        return JsonResponse({'success': True, 'message': 'Horário excluído com sucesso!' })
    return JsonResponse({'success': False, 'message': 'Você não tem permissão para acesso.'}, status=405)
    
@login_required
def pesquisar_horario_por_data(request):
    horario_data = request.GET.get('horario_data', '')
    numero_pagina = request.GET.get('page')
    
    # Converte a data do formato string para o tipo datetime.date
    try:
        data_formatada = datetime.strptime(horario_data, '%Y-%m-%d').date()  # Ajuste o formato conforme necessário
    except ValueError:
        # Retorna uma resposta de erro se a data não for válida
        return JsonResponse({'error': 'Formato de data inválido. Use o formato YYYY-MM-DD.'}, status=400)

    # Filtra os horários pela data
    horarios_lista = Horario.objects.filter(data=data_formatada).order_by('data')

    paginator = Paginator(horarios_lista, settings.NUMBER_GRID_PAGES)
    page_obj = paginator.get_page(numero_pagina)

    return JsonResponse({
        'html': render_to_string('horarios_table.html', {'page_obj': page_obj, 'query': horario_data, 'request': request})
    })

#RELACIONANDO ATIVIDADES COM RESPONSAVEIS (USUARIOS)
@login_required
def adicionar_servico_de_horario(request):
    horario_id = request.POST.get('horario_id')
    servico_id = request.POST.get('servico_id')

    horario = Horario.objects.get(id=horario_id)
    servico = Servico.objects.get(id=servico_id)
    horario.servicos.add(servico)

    # Atualiza a lista de horários após a adição do serviço
    horarios_lista = Horario.objects.all().order_by('data')
    paginator = Paginator(horarios_lista, settings.NUMBER_GRID_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Renderiza o HTML da tabela de horários
    html = render_to_string('horarios_table.html', {'page_obj': page_obj, 'request': request})
    
    return JsonResponse({'success': True, 'message': 'Serviço adicionado com sucesso!', 'html': html})

    
@login_required
def excluir_servico_de_horario(request):
    horario_id = request.POST.get('horario_id')
    servico_id = request.POST.get('servico_id')

    horario = Horario.objects.get(id=horario_id)
    servico = Servico.objects.get(id=servico_id)
    horario.servicos.remove(servico)
    
    return JsonResponse({'success': True, 'message': 'Serviço removido com sucesso!'})

@require_POST    
@login_required
def exibir_servicos_possiveis_para_horario(request):
    horario_id = request.POST.get('txtPostIdServicos')    
    servicos = Servico.objects.order_by('nome')

    servicos_ja_associados = []
    if horario_id:
        horario = Horario.objects.get(id=horario_id)
        servicos_ja_associados = list(horario.servicos.values_list('id', flat=True))

    paginator = Paginator(servicos, settings.NUMBER_GRID_MODAL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'horario_id': horario_id,
        'servicos_ja_associados': servicos_ja_associados
    }
    
    #carrega a pagina de adicao de responsaveis a atividades
    return render(request, 'horarios_add_servicos.html', context)

@login_required
def pesquisar_servico_por_nome_para_horario(request):
    nome = request.GET.get('nome', '')
    page_number = request.GET.get('page', 1)
    horario_id = request.GET.get('horario_id', '')
    servicos = Servico.objects.filter(nome__icontains=nome).order_by('nome')

    servicos_ja_associados = []
    if horario_id:
        horario = Horario.objects.get(id=horario_id)
        servicos_ja_associados = list(horario.servicos.values_list('id', flat=True))

    paginator = Paginator(servicos, settings.NUMBER_GRID_MODAL)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'horario_id': horario_id,
        'servicos_ja_associados': servicos_ja_associados,
        'request': request
    }
    
    #carrega o grid com responsaveis atualizado dentro de atividades_add_responsaveis.html
    html = render_to_string('horarios_add_servicos_table.html', context)
    return JsonResponse({'html': html})

#---------------------------------------------------------------------------------------
#Marcar horário

@login_required
def reservas(request):
    if request.session.get('perfil_atual') not in {'Cliente'}:
        messages.error(request, 'Você não tem permissão para acessar esta página com este perfil.')
        return redirect('core:main')
    
    if request.method == "POST":

        acao = request.POST.get("btnMarcarHorario")

        if acao == "marcar_horario":
            
            horario_id = request.POST.get('txtId')
            horario = Horario.objects.get(id=horario_id)

            if horario.disponivel == False:
                messages.error(request, 'Horário já reservado!')
                return redirect('cadastros:reservas')
            
            else:
                
                horario.disponivel = False
                
                horario.save()

                messages.success(request, 'Horário reservado com sucesso!')
                return redirect('cadastros:reservas')

    horarios_lista = Horario.objects.all().order_by('data')

    paginator = Paginator(horarios_lista, settings.NUMBER_GRID_PAGES)
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)

    return render(request, "escolher_horarios.html", {'page_obj': page_obj})

def escolher_horario(request):
    horario_id = request.GET.get('horario_id')
    horario = Horario.objects.get(id=horario_id)

    if not horario.disponivel:
        return JsonResponse({'success': False, 'message': 'Horário já reservado.'})

    # Reservar o horário
    horario.disponivel = False
    horario.save()

    # Recarregar a lista de horários
    horarios_lista = Horario.objects.all().order_by('data')
    paginator = Paginator(horarios_lista, 10)  # Usando a paginação
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    html = render_to_string('escolher_horarios_table.html', {'page_obj': page_obj, 'request': request})

    return JsonResponse({'success': True, 'html': html})

def get_servicos(request):
    horario = request.GET.get("horario", "")
    servicos = []
    if Horario.objects.filter(horario=horario).exists():
        horario = Horario.objects.get(horario=horario)
        servicos = horario.servicos.all().values("id", "nome")
        data = {"servicos": list(servicos), "horario_existe": True}
    else:
        data = {"horario_existe": False}
    return JsonResponse(data)