from django.core.management.base import BaseCommand
from django.db import connection, transaction
from cadastros.models import Perfil, Usuario


class Command(BaseCommand):
    help = "Redefine o sistema, apagando todos os dados do app cadastros e recriando os dados padrões."

    @transaction.atomic
    def handle(self, *args, **options):
        cursor = connection.cursor()
        # obtem apenas as tabelas do aplicativo cadastros
        app_labels = ["cadastros"]
        tables = [
            table
            for table in connection.introspection.table_names()
            if any(app in table for app in app_labels)
        ]

        # desabilita as constraints de chave estrangeira para postgres
        if connection.vendor == "postgresql":
            for table in tables:
                cursor.execute(f'ALTER TABLE "{table}" DISABLE TRIGGER ALL;')

        # apaga todos os dados das tabelas do aplicativo
        for table in tables:
            cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')

        # reseta as sequencias de autoincremento
        if connection.vendor == "postgresql":
            for table in tables:
                cursor.execute(
                    f"""
                    SELECT setval(pg_get_serial_sequence('"{table}"', 'id'), 1, false)
                    WHERE EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='{table}' AND column_name='id'
                        AND column_default LIKE 'nextval%'
                    );
                """
                )

        # reabilita as constraints de chave estrangeira para postgres
        if connection.vendor == "postgresql":
            for table in tables:
                cursor.execute(f'ALTER TABLE "{table}" ENABLE TRIGGER ALL;')

        # cria os perfis necessarios
        perfil_prop = Perfil(id=1, nome="Propietário")
        perfil_prop.save(force_insert=True)

        perfil_func = Perfil(id=2, nome="Funcionário")
        perfil_func.save(force_insert=True)

        perfil_cliente = Perfil(id=3, nome="Cliente")
        perfil_cliente.save(force_insert=True)

        # adiciona o superusuario
        if not Usuario.objects.filter(
            email="joaodirceuconstantinocarvalho@gmail.com"
        ).exists():
            usuario = Usuario(
                id=1,
                email="joaodirceuconstantinocarvalho@gmail.com",
                nome="Propietário",
                is_admin=True,
            )
            usuario.set_password("123456")
            usuario.save(force_insert=True)
            usuario.perfis.add(perfil_prop)
            usuario.save()

        self.stdout.write(self.style.SUCCESS("Banco de dados redefinido com sucesso!"))
