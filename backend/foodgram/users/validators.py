import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value.lower() == 'плохое имя':
        raise ValidationError(
            'Недопустимое имя пользователя!'
        )
    if not bool(re.match(r'^[\w.@+-]+$', value)):
        raise ValidationError(
            'Некорректные символы в имени пользователя'
        )
    return value
