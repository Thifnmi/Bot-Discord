import os
import json
from dotenv import load_dotenv
from decimal import Decimal

# load all environment from .env file. it 'll overwrite to use env
# variable directly from os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "..", ".env"))


def _get_config_value(key, default_value=None):
    value = os.environ.get(key, default_value)
    if (value is not None and value != "") and isinstance(value, str):
        if value.isdigit():
            value = int(value)
        elif isinstance(value, str) and key.endswith("LIST"):
            value = json.loads(value)

    return value


class BaseConfig(object):
    """..."""

    TOKEN = _get_config_value("TOKEN", "MyKey")
    COVID19 = _get_config_value("COVID19", "https://thifnmi.com")


class DevelopmentConfig(BaseConfig):
    """..."""

    ENV = "development"

    pass


class StagingConfig(BaseConfig):
    """..."""

    ENV = "staging"

    pass

class Staging2Config(BaseConfig):
    """..."""

    ENV = "staging2"

    pass


class ProductionConfig(BaseConfig):
    """..."""

    ENV = "production"

    pass


config = {
    "production": ProductionConfig,
    "staging": StagingConfig,
    "development": DevelopmentConfig,
}
