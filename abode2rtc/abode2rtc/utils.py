import uuid


DEVICE_ID_PATH = '/data/abode_device_id'


def generate_uuid() -> str:
    """
    Returns this add-on's Abode device ID: a 32-character string with no dashes.

    Created once and kept in /data so every login comes from the same device.
    A new random ID per login made Abode email a "new sign-in" alert each time.
    """
    try:
        with open(DEVICE_ID_PATH) as f:
            device_id = f.read().strip()
        if len(device_id) == 32:
            return device_id
    except OSError:
        pass
    device_id = str(uuid.uuid4()).replace('-', '')
    try:
        with open(DEVICE_ID_PATH, 'w') as f:
            f.write(device_id)
    except OSError:
        pass
    return device_id


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
