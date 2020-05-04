import sys
from os import environ, chdir


def _resources_redirect_protocol():
    environ['KIVY_NO_FILELOG'] = '1'
    environ['KIVY_NO_CONSOLELOG'] = '1'
    environ['KIVY_NO_ENV_CONFIG'] = '1'

    if getattr(sys, 'frozen', False):
        chdir(sys._MEIPASS)

_resources_redirect_protocol()


if __name__ == '__main__':
    from utils.loggers import alert_
    from utils.protocols import startup_protocol
    startup_protocol()  # engaging startup routine

    from kivy.app import App
    from viewscontrollers.v3play.v3play import V3Play


    class syaiV3PlayApp(App):
        title = 'syaiV3play'
        use_kivy_settings = False

        def build(self):
            self.root = V3Play()
            return self.root


    syaiV3PlayApp().run()
