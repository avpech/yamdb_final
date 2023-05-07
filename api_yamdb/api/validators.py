from collections import OrderedDict
from typing import Union

from rest_framework.serializers import ValidationError


def me_name_forbidden(
        data: OrderedDict
) -> Union[OrderedDict, ValidationError]:
    """Проверка на невозможность использования имени пользователя "me"."""
    if data.get('username') == 'me':
        raise ValidationError(
            {'username': 'Недопустимое имя пользователя'}
        )
    return data
