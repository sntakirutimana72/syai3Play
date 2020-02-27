import sys
from os import chdir, environ
from kivy.config import Config
from utils.read_config import read_config
from utils.helpers import digit_string_2_array


def startup():
    environ['KIVY_NO_FILELOG'] = '1'
    environ['KIVY_NO_CONSOLELOG'] = '1'
    environ['KIVY_NO_ENV_CONFIG'] = '1'

    def _resources_redirect():
        if getattr(sys, 'frozen', False):
            chdir(sys._MEIPASS)

    def _apply_defaults():
        for option, value in read_config('window'):
            if option in ('size', 'position'):
                converted_arr = digit_string_2_array(value)
                sub_option_1, sub_option_2 = ['width', 'height'] if option == 'size' else ['left', 'top']
                Config.set('graphics', sub_option_1, f'{converted_arr[0]}')
                Config.set('graphics', sub_option_2, f'{converted_arr[1]}')
            else:
                Config.set('graphics', option, value)

    _resources_redirect()
    _apply_defaults()
