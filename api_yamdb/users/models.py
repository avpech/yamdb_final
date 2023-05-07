from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователей."""
    ROLES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True
    )
    role = models.CharField(
        verbose_name='Роль пользователя',
        max_length=10,
        choices=ROLES,
        default='user'
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True,
        help_text='Обязательное поле.',
        db_index=True
    )

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = (
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='username_me_forbidden'
            ),
        )
        ordering = ('date_joined',)
