from dataclasses import dataclass
from typing import Union

from utils.exception import ValidationException


class BaseValidator:

    def validate(self, key, value):
        raise NotImplementedError

    def __call__(self, key, value, *args, **kwargs):
        return self.validate(key, value)


class RequiredValidator(BaseValidator):

    def validate(self, key, value):
        if value is None:
            raise ValidationException('Поле {} должно быть обязательным'.format(key))
        return True


class AuthKeyValidator(BaseValidator):

    def __init__(self, key):
        self.key = key

    def validate(self, key, value):
        if value != self.key:
            raise ValidationException('Неверные данные для авторизации')
        return True


class TypeValidator(BaseValidator):

    def __init__(self, default_type):
        self.type = default_type

    def validate(self, key, value):
        if type(value) != self.type:
            raise ValidationException(f'Значение должно быть {self.type}')
