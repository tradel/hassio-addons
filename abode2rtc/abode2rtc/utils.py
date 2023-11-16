import uuid


def generate_uuid() -> str:
    """
    Generates a random UUID in the format expected by Abode, which is a 32-character string with no dashes.
    """
    return str(uuid.uuid4()).replace('-', '')


def obscure_passwords(data: dict) -> dict:
    """
    Removes passwords and API tokens from a dict, replacing them with asterisks. Used when logging so
    we don't accidentally leak credentials.
    """
    options = data.copy()
    for key, val in options.items():
        if 'password' in key:
            options[key] = '**********'
        elif key == 'Authorization':
            options[key] = 'Bearer **********'
    return options
