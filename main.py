if __name__ == '__main__':
    import sys
    from kivy.app import App
    from utils.views import LevelBar
    from kivy.uix.floatlayout import FloatLayout

    class V3PlayApp(App):
        title = 'syai-V3Play'
        use_kivy_settings = False

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
