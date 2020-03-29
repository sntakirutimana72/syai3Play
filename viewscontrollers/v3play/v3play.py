from kivy.app import App
from os.path import join
from kivy.clock import Clock
from kivy.lang import Builder
from guix.templates import BoxLayer
from guix.headbar import AppHeadBar
from utils.read_config import read_config
from kivy.uix.gridlayout import GridLayout
from utils.helpers import digit_string_2_array

Builder.load_file(join('viewscontrollers', 'v3play', 'v3play.kv'))


class LeftMenuNavigator(BoxLayer):
    pass


class LeftMenuElement(GridLayout):
    pass


class V3Play(BoxLayer):

    def __init__(self, **kwargs):
        super(V3Play, self).__init__(**kwargs)
        self._apply_configsOn_startup()

    def _apply_configsOn_startup(self):
        """ configuring main app view with pre-saved settings """

        back_color = read_config('main', 'back_color')
        self.background_color = digit_string_2_array(back_color, float)

    def process_cli_inputs(self, *largs):
        """ Capture all inputs from command line on startup """
        print(largs)

    def _ready_routine(self):
        """ called after startup dynamic resizing completes """
        pass

    def _activate_dragAndDrop_tunnel(self):
        _root_window = App.get_running_app().root_window
        _root_window.bind(on_dropfile=self._processing_dropped_file)

    def _processing_dropped_file(self, *largs):
        if self.dropping is None:
            # mapping a dropping status widget
            self.show_dropping_status()
            # creating after dropping counter measure
            self.dropping = Clock.schedule_once(self.after_all_dropped, 1.4)
        # freezing after dropping counter measure just to sort a dropped file
        self.dropping.cancel()
        # decoding dropped file to <class str>
        dropped_file = largs[1].decode('utf-8')
        self.verify_file_address(dropped_file)
        # unfreeze after dropping counter measure
        self.dropping()
