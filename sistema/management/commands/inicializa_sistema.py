from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from cadastros.models import Perfil


# funcao para inicializar o sistema com os dados padrão
class Command(BaseCommand):
    help = "Inicializa o sistema com os dados padrão"

    def handle(self, *args, **options):

        # cria os perfis necessarios
        perfil_prop, created = Perfil.objects.get_or_create(id=1, nome="Proprietário")
        if created:
            self.stdout.write(self.style.SUCCESS(f"Perfil criado: {perfil_prop.nome}"))

        perfil_func, created = Perfil.objects.get_or_create(id=2, nome="Funcionário")
        if created:
            self.stdout.write(self.style.SUCCESS(f"Perfil criado: {perfil_func.nome}"))

        perfil_cliente, created = Perfil.objects.get_or_create(id=3, nome="Cliente")
        if created:
            self.stdout.write(
                self.style.SUCCESS(f"Perfil criado: {perfil_cliente.nome}")
            )

        # cria o superusuario
        User = get_user_model()
        if not User.objects.filter(
            email="joaodirceuconstantinocarvalho@gmail.com"
        ).exists():
            usuario = User(
                email="joaodirceuconstantinocarvalho@gmail.com@gmail.com",
                nome="Proprietário",
                telefone="00000000000",
                is_admin=True,
            )
            usuario.set_password("123456")
            usuario.save()

            usuario.perfis.add(perfil_prop)
            usuario.save()
            self.stdout.write(self.style.SUCCESS("Superusuário criado com sucesso!"))
        else:
            self.stdout.write(
                self.style.WARNING("Superusuário já existe. Nenhuma ação foi tomada.")
            )
