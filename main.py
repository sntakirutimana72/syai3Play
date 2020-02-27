from kivy.app import App


class MainApp(App):
    title = 'SYAI3Play'
    use_kivy_settings = False

    def build(self):
        return SplashScreen() if _mainRoot_ else MainRoot()

    def on_start(self):
        pass

    def on_minimize(self):
        pass

    def on_restore(self):
        pass

    def on_maximize(self):
        pass

    def on_stop(self, *largs):
        try:
            self.config.read(path.join(self.directory, 'settings.ini'))
            self.config["window"]["window"] = json.dumps({
                'window-size': [450, 128],
                'window-pos': [Window.left, Window.top]
            })
            self.config.write()
        except:
            Logger.error("SYAI3Play: CONFIG")

        sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        _mainRoot_ = MainRoot()
        _mainRoot_.playlist_fromCLI(sys.argv[1:])

    MainApp().run()
