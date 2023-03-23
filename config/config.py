from json import load

from schemas import ConfigSchema, ConfigTextSchema


def load_config() -> ConfigSchema:
    with open("config.json", "r", encoding="utf-8") as file:
        return ConfigSchema(**load(file))


def load_config_text() -> ConfigTextSchema:
    with open("config_text.json", "r", encoding="utf-8") as file:
        return ConfigTextSchema(**load(file))


CONFIG: ConfigSchema = load_config()
CONFIGTEXT: ConfigTextSchema = load_config_text()
