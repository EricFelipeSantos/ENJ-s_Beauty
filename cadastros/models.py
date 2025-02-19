from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.deletion import ProtectedError

class Perfil(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    def delete(self, *args, **kwargs):
        if self.usuario_set.exists():
            raise ProtectedError(
                "Não é possível excluir este perfil, pois ele possui usuarios vinculados.",
                self,
            )
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nome


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None):
        if not email:
            raise ValueError("O usuário deve ter um endereço de e-mail")
        user = self.model(email=self.normalize_email(email), nome=nome)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None):
        user = self.create_user(email, nome, password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Usuario(AbstractBaseUser):
    nome = models.CharField(max_length=300)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    telefone = models.CharField(max_length=11)
    perfis = models.ManyToManyField(Perfil)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def tem_perfil(self, perfil_nome):
        return self.perfis.filter(nome=perfil_nome).exists()


class Servico(models.Model):
    nome = models.CharField(max_length=300)
    responsaveis = models.ManyToManyField('Usuario', related_name='responsaveis')
    valor = models.FloatField()

    def __str__(self):
        return self.nome

class Horario(models.Model):
    data = models.DateField()  
    hora = models.TimeField()
    servicos = models.ManyToManyField('Servico', related_name='servico')
    disponivel = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.data.strftime("%d/%m/%Y") + " " + self.hora.strftime("%H:%M")
