from django.db.models import DecimalField


def PostgresDecimalField(*args, **kwargs):
    """Custom decimal field.

    """
    return DecimalField(max_digits=65535, decimal_places=12, *args, **kwargs)
