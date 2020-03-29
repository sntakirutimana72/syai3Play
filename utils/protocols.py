from kivy.config import Config
from pyautogui import size as pysize
from utils.read_config import read_config


def startup_protocol():
    """ configuring window preload settings from configuration file """
    
    for option, value in read_config('window'):
        if option == 'size_ratio':
            size_ratio = float(value)
            width, height = pysize()  # retrieving system size
            ration_width = int(width * size_ratio)  # render width to 88%
            ration_height = int(height * size_ratio)  # render height to 88%

            left = int((width - ration_width) * .5)  # x-axis
            top = int((height - ration_height) * .5) - 20  # y-axis

            Config.set('graphics', 'minimum_width', f'{ration_width}')
            Config.set('graphics', 'minimum_height', f'{ration_height}')
            Config.set('graphics', 'width', f'{ration_width}')
            Config.set('graphics', 'height', f'{ration_height}')
            Config.set('graphics', 'left', f'{left}')
            Config.set('graphics', 'top', f'{top}')
        else:
            Config.set('graphics', option, value)
