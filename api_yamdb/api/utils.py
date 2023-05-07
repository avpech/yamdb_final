from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def send_confirmation_code(user: AbstractBaseUser) -> None:
    """Создание и отправка кода подтверждения на email пользователя."""
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Confirmation code',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.NOREPLY_EMAIL,
        recipient_list=(user.email,)
    )


def get_token(to_check: str,
              user: AbstractBaseUser,
              ) -> Tuple[Optional[RefreshToken], bool]:
    """Проверка кода подтверждения и создание jwt-токена в случае успеха."""
    if default_token_generator.check_token(user, to_check):
        token = RefreshToken.for_user(user)
        return token.access_token, True
    return None, False
