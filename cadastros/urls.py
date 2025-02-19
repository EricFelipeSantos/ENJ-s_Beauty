from django.urls import path
from . import views

app_name = 'cadastros'

urlpatterns = [

    path("usuarios/", views.usuarios, name="usuarios"),
    path('verificar_email/', views.verificar_email, name='verificar_email'),
    path('obter_usuario_por_id/', views.obter_usuario_por_id, name='obter_usuario_por_id'),
    path('excluir_usuario/', views.excluir_usuario, name='excluir_usuario'),
    path('pesquisar_usuario_por_nome/', views.pesquisar_usuario_por_nome, name='pesquisar_usuario_por_nome'),

    path('servicos/', views.servicos, name='servicos'),
    path('obter_servico_por_id/', views.obter_servico_por_id, name='obter_servico_por_id'),
    path('excluir_servico/', views.excluir_servico, name='excluir_servico'),
    path('pesquisar_servico_por_nome/', views.pesquisar_servico_por_nome, name='pesquisar_servico_por_nome'),

    path('adicionar_responsavel_de_servico/', views.adicionar_responsavel_de_servico, name='adicionar_responsavel_de_servico'),
    path('excluir_responsavel_de_servico/', views.excluir_responsavel_de_servico, name='excluir_responsavel_de_servico'),
    path('exibir_responsaveis_possiveis_para_servico/', views.exibir_responsaveis_possiveis_para_servico, name='exibir_responsaveis_possiveis_para_servico'),
    path('pesquisar_responsavel_por_nome_para_servico/', views.pesquisar_responsavel_por_nome_para_servico, name='pesquisar_responsavel_por_nome_para_servico'),

    path('horarios/', views.horarios, name='horarios'),
    path('obter_horario_por_id/', views.obter_horario_por_id, name='obter_horario_por_id'),
    path('excluir_horario/', views.excluir_horario, name='excluir_horario'),
    path('pesquisar_horario_por_data/', views.pesquisar_horario_por_data, name='pesquisar_horario_por_data'),

    path('adicionar_servico_de_horario/', views.adicionar_servico_de_horario, name='adicionar_servico_de_horario'),
    path('excluir_servico_de_horario/', views.excluir_servico_de_horario, name='excluir_servico_de_horario'),
    path('exibir_servicos_possiveis_para_horario/', views.exibir_servicos_possiveis_para_horario, name='exibir_servicos_possiveis_para_horario'),
    path('pesquisar_servico_por_nome_para_horario/', views.pesquisar_servico_por_nome_para_horario, name='pesquisar_servico_por_nome_para_horario'),
    
    path('resevas/', views.reservas, name='reservas'),
    path('escolher_horario/', views.escolher_horario, name='escolher_horario'),
    path('get_servicos/', views.get_servicos, name='get_servicos'),
]



