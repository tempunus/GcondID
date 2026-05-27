from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("O email e obrigatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_approved", True)
        extra_fields.setdefault("access_level", User.AccessLevel.ADMIN)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class AccessLevel(models.TextChoices):
        ADMIN = "admin", "Administrador"
        FUNCIONARIO = "funcionario", "Funcionario"
        VISITANTE = "visitante", "Visitante/Restrito"

    email = models.EmailField("email", unique=True)
    phone = models.CharField("telefone/whatsapp", max_length=20, blank=True)
    access_level = models.CharField(
        "nivel de acesso",
        max_length=20,
        choices=AccessLevel.choices,
        default=AccessLevel.VISITANTE,
    )
    is_approved = models.BooleanField("aprovado", default=False)
    is_blocked = models.BooleanField("bloqueado", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def can_access_panel(self):
        return self.is_active and self.is_approved and not self.is_blocked

    @property
    def is_gcondid_admin(self):
        return self.is_superuser or self.access_level == self.AccessLevel.ADMIN

    @property
    def display_name(self):
        return self.get_full_name() or self.first_name or f"Usuario #{self.pk}"

    def __str__(self):
        return self.display_name

# Create your models here.
