from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.validators import RegexValidator


class CustomAccountManager(BaseUserManager):
    def create_user(
            self, email, username,
            first_name, last_name,
            password, **other_fields
    ):
        email = self.normalize_email(email)
        user = self.model(
            email=email, username=username,
            first_name=first_name, last_name=last_name,
            **other_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self, email, username,
            first_name, last_name,
            password, **other_fields
    ):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        return self.create_user(
            email, username,
            first_name, last_name,
            password, **other_fields
        )


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=254, unique=True, verbose_name='Email Adress'
    )
    username = models.CharField(
        max_length=150, unique=True,
        verbose_name='Username',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$', message='Username have banned symbols!'
            )
        ]
    )
    first_name = models.CharField(
        max_length=150, verbose_name='First name'
    )
    last_name = models.CharField(
        max_length=150, verbose_name='Last name'
    )
    password = models.CharField(
        max_length=150, verbose_name='Password'
    )
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password', 'email', 'first_name', 'last_name']
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = CustomAccountManager()

    class Meta:
        ordering = ['-id']

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        CustomUser,
        related_name='subscriber',
        verbose_name='Subcriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        CustomUser,
        related_name='subscribing',
        verbose_name='Author',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique following'
            )
        ]

    def __str__(self) -> str:
        return f'{self.user.username} - {self.author.username}'
