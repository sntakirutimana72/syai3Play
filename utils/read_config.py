from os import path
from utils.app_envs import appDataDir
from configparser import ConfigParser


def read_config(section, option=None):
    try:
        config_settings = ConfigParser()
        config_settings.read(path.join(appDataDir(), 'settings.ini'))
        return config_settings.get(section, option) if option else config_settings.items(section)
    except:
        pass