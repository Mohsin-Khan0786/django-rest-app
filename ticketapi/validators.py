from django.core.exceptions import ValidationError


def validate_phone(value):
    if not value.startswith("+92") or len(value) != 13:
        raise ValidationError("Phone number must start with +92 and contain 13 digits")
