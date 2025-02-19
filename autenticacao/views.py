from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from cadastros.models import Usuario
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


def login(request):
    if request.method == "POST":
        email = request.POST.get("txtEmail")
        senha = request.POST.get("txtSenha")
        perfil_id = request.POST.get("slcPerfil")

        usuario = authenticate(request, username=email, password=senha)

        if usuario is not None and perfil_id:
            perfis_usuario = usuario.perfis.filter(id=perfil_id)
            if perfis_usuario.exists():
                # limpa as sessoes do usuario
                request.session.flush()
                # cria a sessao do usuario
                auth_login(request, usuario)

                request.session["id_atual"] = usuario.id
                request.session["email_atual"] = usuario.email
                request.session["perfil_atual"] = perfis_usuario.first().nome
                request.session["perfis"] = list(
                    usuario.perfis.values_list("nome", flat=True)
                )

                # configura sessao para expirar em 4 horas
                request.session.set_expiry(14400)

                messages.success(request, "Login realizado com sucesso!")

                # pode separar em diferentes paginas ou alterar os links da main
                if request.session.get("perfil_atual") in {
                    "Cliente",
                    "Funcionário",
                    "Proprietário",
                }:
                    return redirect("core:main")

            else:
                messages.error(request, "Perfil inválido para este usuário.")
        else:
            if usuario is None:
                messages.error(request, "Senha incorreta.")
            else:
                messages.error(request, "Usuário ou senha inválidos.")

    return render(request, "login.html")


def get_perfis(request):
    email = request.GET.get("email", "")
    perfis = []
    if Usuario.objects.filter(email=email).exists():
        usuario = Usuario.objects.get(email=email)
        perfis = usuario.perfis.all().values("id", "nome")
        data = {"perfis": list(perfis), "usuario_existe": True}
    else:
        data = {"usuario_existe": False}
    return JsonResponse(data)


def logout(request):
    # limpa a sessao ao deslogar
    request.session.flush()
    auth_logout(request)

    messages.success(request, "Logout realizado com sucesso.")
    return redirect("autenticacao:login")


from django.templatetags.static import static


def recuperar_senha(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            usuario = Usuario.objects.get(email=email)
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))

            # Gera a URL de redefinição de senha
            reset_url = request.build_absolute_uri(
                reverse(
                    "autenticacao:reset_senha", kwargs={"uidb64": uid, "token": token}
                )
            )

            # Obtém a URL absoluta da imagem
            logo_url = request.build_absolute_uri(static("img/enjs_fundo_branco.jpg"))

            # Renderiza o template HTML do e-mail, passando a URL da imagem
            html_content = render_to_string(
                "recuperar_senha_email.html",
                {"reset_url": reset_url, "logo_url": logo_url},
            )

            # Envia o e-mail em HTML
            msg = EmailMultiAlternatives(
                "Recuperação de senha - ENJ's Beauty",
                "Redefina sua senha clicando no link: {}".format(reset_url),
                "seu_email@dominio.com",
                [email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return JsonResponse(
                {"success": True, "message": "Email enviado com o link de redefinição."}
            )
        except Usuario.DoesNotExist:
            return JsonResponse({"success": False, "message": "Email não encontrado."})
    return JsonResponse({"success": False, "message": "Método inválido."})


def redefinir_senha(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        usuario = Usuario.objects.get(pk=uid)

        if default_token_generator.check_token(usuario, token):
            if request.method == "POST":
                nova_senha = request.POST.get("nova_senha")
                usuario.set_password(nova_senha)
                usuario.save()
                messages.success(request, "Senha alterada com sucesso!")
                return redirect("autenticacao:login")

            return render(request, "reset_senha.html", {"valid_token": True})

        else:
            return render(request, "reset_senha.html", {"valid_token": False})

    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        return render(request, "reset_senha.html", {"valid_token": False})
