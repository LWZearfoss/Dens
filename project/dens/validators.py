from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from better_profanity.profanity import contains_profanity

from .models import DenModel


def validate_unique_user_email(value):
    user_objects = User.objects.filter(email=value)
    if len(user_objects) > 0:
        raise ValidationError("A user with that email already exists.")


def validate_den_name_not_empty(value):
    if not value or value.isspace():
        raise ValidationError("The den name must be non-empty.")


def validate_den_name_length(value):
    if len(value) > 24:
        raise ValidationError(
            "The den name must not be longer than 24 characters.")


def validate_unique_den_name(value):
    den_objects = DenModel.objects.filter(name=value)
    if len(den_objects) > 0:
        raise ValidationError("A den with that name already exists.")


def validate_den_name_not_profane(value):
    if contains_profanity(value):
        raise ValidationError("The den name must not contain profanity.")


def validate_message_length(value):
    if len(value) > 240:
        raise ValidationError(
            "The message must not be longer than 24 characters.")


def validate_message_not_profane(value):
    if contains_profanity(value):
        raise ValidationError("The message must not contain profanity.")


def validateField(value, validators=[]):
    errors = []
    for validator in validators:
        try:
            validator(value)
        except ValidationError as e:
            errors.append(str(e)[2:-2])
    return errors
