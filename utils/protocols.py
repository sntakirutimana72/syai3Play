import sys
from os import chdir, environ
from kivy.config import Config
from pyautogui import size as pysize
from utils.read_config import read_config
from utils.helpers import digit_string_2_array


def startup_protocol():
    environ['KIVY_NO_FILELOG'] = '1'
    environ['KIVY_NO_CONSOLELOG'] = '1'
    environ['KIVY_NO_ENV_CONFIG'] = '1'

    def _resources_redirect():
        if getattr(sys, 'frozen', False):
            chdir(sys._MEIPASS)

    def _apply_defaults():
        for option, value in read_config('window'):
            if option == 'size_ratio':
                size_ratio = float(value)
                width, height = pysize()  # retrieving system size
                ration_width = int(width * size_ratio)  # render width to 88%
                ration_height = int(height * size_ratio)  # render height to 88%

                left = int((width - ration_width) * .5)  # x-axis
                top = int((height - ration_height) * .5) - 20 # y-axis

                Config.set('graphics', 'width', f'{ration_width}')
                Config.set('graphics', 'height', f'{ration_height}')
                Config.set('graphics', 'left', f'{left}')
                Config.set('graphics', 'top', f'{top}')
            else:
                Config.set('graphics', option, value)

    _resources_redirect()
    _apply_defaults()
