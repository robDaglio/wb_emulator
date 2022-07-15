import os
from random import choice, randint
import logging

VERSION_PROPERTIES = os.path.join(os.getcwd(), 'version.properties')
API_PROPERTIES = os.path.join(os.getcwd(), 'api.properties')


def generate_random_mac():
    chars = [str(x) for x in range(10)] + [chr(x) for x in range(65, 71)]
    return ':'.join([f'{randint(0, 9)}{choice(chars)}' for _ in range(6)])


def read_properties_file(properties_file: str) -> str:
    try:
        with open(properties_file, 'r') as f:
            version = f.read()
            return version.split('=')[-1] if '=' in version else version
    except (FileNotFoundError, IOError) as e:
        logging.exception(f'Unable to read properties file:\n{e}')
        return 'na'
