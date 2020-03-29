from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from utils.loggers import alert_
from kivy.uix.boxlayout import BoxLayout
from utils.read_config import read_config
from guix.customlayers import SquaredLogo
from utils.helpers import digit_string_2_array
from kivy.properties import NumericProperty, StringProperty, ListProperty, OptionProperty
from guix.templates import IconFullPath, ButtonTemplate, Dragging, Hovering, BoxLayer


Builder.load_string("""
<HCloseButton>:
    canvas:
        PushMatrix
        Color:
            rgba: (.12, .12, .15, self.toggle_graffiti)
        Rotate:
            angle: self.angle
            origin: self.center
        SmoothLine:
            width: 1.1
            points: (self.center_x, self.y + dp(4), self.center_x, self.top - dp(4))
        SmoothLine:
            width: 1.1
            points: (self.x + dp(4), self.center_y, self.right - dp(4), self.center_y)
    canvas.after:
        PopMatrix


<HMinimizeButton>:
    canvas:
        Color:
            rgba: (.12, .12, .15, self.toggle_graffiti)
        SmoothLine:
            points: (self.x + dp(4), self.center_y, self.right - dp(4), self.center_y)


<HeadBarDescription>:
    markup: True
    shorten: True
    valign: 'middle'
    font_size: '13sp'
    text_size: self.size
    font_name: 'Roboto-Bold'


<HeadBarControlsContainer>:
    size_hint_x: None
    width: dp(70)
    spacing: '8sp'
    padding: 0, '6sp'

    HMinimizeButton:
        id: minimize
        toggle_graffiti: root.toggle_graffiti if not self.disabled else .1
        on_release: root.on_minimize()
    HResizeButton:
        id: resize
        toggle_graffiti: root.toggle_graffiti if not self.disabled else .1
        on_release: root.on_resize()
    HCloseButton:
        id: close
        toggle_graffiti: root.toggle_graffiti
        on_release: root.on_close()


<HeadBar>:
    size_hint_y: None
    height: dp(34)
    spacing: '6sp'
    padding: '10sp', '2sp'

    # logo & title UIx
    BoxLayout:
        id: app_desc

        # Logo-part
        HeadBarLogoInterface:
            id: h_logo
            icon_name: root.logo_name

        # Title-part
        HeadBarDescription:
            text: root.title
            color: root.title_color

    HeadBarControlsContainer:
        id: header_controls
        disable_controls: root.disable_controls
""")


class HeadBarDescription(Label):
    pass


class HeadBarLogoInterface(SquaredLogo, IconFullPath):
    pace = 4
    cover_color = [.3, .3, .35, 1]


class HeadBarButtonInterface(ButtonTemplate):
    border_radius = [3]
    toggle_graffiti = NumericProperty(0)

    def on_hover(self):
        if not self.disabled:
            self.background_color = [1, 1, 1, .1]

    def on_leave(self):
        if not self.disabled:
            self.background_color = [0, 0, 0, 0]

    def on_release(self):
        pass


class HCloseButton(HeadBarButtonInterface):
    angle = NumericProperty(45)


class HMinimizeButton(HeadBarButtonInterface):
    pass


class HResizeButton(HCloseButton):
    angle = 0


class HeadBarControlsContainer(BoxLayout, Hovering):
    toggle_graffiti = NumericProperty(.2)
    disable_controls = OptionProperty('', options=['', '&ri', '&mi', 'mi&ri'])

    def on_hover(self):
        self.toggle_graffiti = 1

    def on_leave(self):
        self.toggle_graffiti = .2

    def on_close(self):
        self.parent.dispatch('on_close')

    def on_resize(self):
        self.parent.dispatch('on_resize')

    def on_minimize(self):
        self.parent.dispatch('on_minimize')

    def on_disable_controls(self, interface, disabler):
        if disabler in ['&ri', 'mi&ri']:
            self.ids.resize.disabled = True
        elif disabler in ['&mi', 'mi&ri']:
            self.ids.minimize.disabled = True


class HeadBar(BoxLayer, Dragging):
    title = StringProperty('')
    logo_name = StringProperty('')
    title_color = ListProperty([1, 1, 1, 1])
    disable_controls = OptionProperty('', options=['', '&ri', '&mi', 'mi&ri'])

    def __init__(self, **kwargs):
        self.register_event_type('on_close')
        self.register_event_type('on_resize')
        self.register_event_type('on_minimize')
        super(HeadBar, self).__init__(**kwargs)
        self._apply_configs()

    def _apply_configs(self):
        pass

    def on_close(self):
        pass

    def on_resize(self):
        pass

    def on_minimize(self):
        pass


class AppHeadBar(HeadBar):
    draggable_obj = 'app'

    def _apply_configs(self):
        try:
            for option, value in read_config('headbar'):
                if option == 'title':
                    self.title = value
                elif option == 'logo':
                    self.logo_name = value
                else:
                    color = digit_string_2_array(value, float)
                    if option == 'font_color':
                        self.title_color = color
                    else:
                        self.background_color = color
        except Exception as exc:
            alert_(exc)

    def on_minimize(self):
        # application minimizing method
        App.get_running_app().root_window.minimize()

    def on_resize(self):
        # application resizing method
        pass

    def on_close(self):
        # application closing method
        App.stop(App.get_running_app())
