if __name__ == '__main__':
    from utils.protocols import startup_protocol
    startup_protocol()  # engaging startup routine

    import sys
    from kivy.app import App
    from views.views import SyaiV3Play


    class V3PlayApp(App):
        title = 'syai V3Play'
        use_kivy_settings = False

        def build(self):
            self.root = SyaiV3Play()
            return self.root

        def on_start(self):
            pass

        def on_restore(self):
            pass

        def on_minimize(self):
            pass

        def on_maximize(self):
            pass

        def on_stop(self, *largs):
            pass


    V3PlayApp().run()
