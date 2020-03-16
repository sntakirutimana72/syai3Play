from kivy.lang import Builder
from guix.templates import Hovering
from guix.customlayers import CustomLayer
from kivy.properties import ListProperty, BooleanProperty, \
    StringProperty, OptionProperty, NumericProperty


Builder.load_string("""
<LevelBar>:
    canvas:
        Color:
            rgba: self.level_color
        RoundedRectangle:
            radius: self.radius
            pos: self.x + dp(1.5), self.y + dp(1.5)
            size: dp(self.level - 3), self.size[1] - dp(3)

        Color:
            rgba: self.handle_color
        Ellipse:
            pos: (self.x + dp(self.level - (self.height + 10) / 2), self.y - dp(5))
            size: (self.height + dp(10), self.height + dp(10))
            source: self.handle_image
""")


class LevelBar(CustomLayer, Hovering):
    handle_color = ListProperty([.2, .2, .25, 1])
    handle_image = StringProperty('icons/yellow.png')

    level = NumericProperty(0.)
    level_color = ListProperty([0, .4, .3, .6])
    _recent_level = NumericProperty(0.)  # Track bar final level in percentage 0.0% after all motion events

    visible = OptionProperty('show', options=['show', 'hide'])  # clocking capability
    bar_active = BooleanProperty(True)  # Disables & Enables interactions with the handle
    auto_visibility_switch = None  # Automates the visibility mode switching when :attr::visible::`is enabled`
    _width_tether = None
    """ last width to be used when auto resize triggered  in order to re-normalize level """

    def __init__(self, **kwargs):
        self.register_event_type('on_final_point')
        super(LevelBar, self).__init__(**kwargs)
        self.background_color = [.06, .03, 0, .4]

    def on_hover(self):
        if self.disabled or self.visible == 'show':
            return
        self._camelfraging()

    def on_leave(self):
        if self.disabled or self.visible == 'show':
            return
        self._camelfraging()

    def on_size(self, interface, size):
        if not self.level:
            self._width_tether = size[0]
            return
        self.re_normalize_levels()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if self.bar_active:
                touch.grab(self)
                self._normalize_levels_(touch.pos[0])
            return True
        return super(LevelBar, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self._normalize_levels_(touch.pos[0])
        return True

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            self._compute_final_levels(touch.pos[0])
            self.dispatch('on_final_point')
            touch.ungrab(self)
        return True

    def on_bar_active(self, interface, value):
        self._toggle_handle(value)
        self.disabled = value

    def on_visible(self, interface, value):
        if value == 'hide':
            if self.auto_visibility_switch:
                self.auto_visibility_switch.cancel()
                self.auto_visibility_switch = None
            self._toggle_handle(False)
        else:
            if self.auto_visibility_switch is None:
                self.auto_visibility_switch = Clock.schedule_once(self._camelfraging, 5)
            else:
                self._toggle_handle(True)

    def _camelfraging(self, *largs):
        self.visible = 'hide' if largs else 'show'

    def _toggle_handle(self, value):
        self.handler_normal[-1] = 1 if value else 0

    def _normalize_levels_(self, pos_x):
        self.level = self._compute_levels(pos_x)

    def _compute_final_levels(self, pos_x):
        self._recent_level = self._compute_levels(pos_x)

    def _compute_levels(self, pos_x):
        x = pos_x - self.x
        if x < 0:
            x = 0
        elif x > self.size[0]:
            x = self.size[0]
        return x

    def re_normalize_levels(self):
        self.level *= self.size[0] / self._width_tether
        self._width_tether = self.size[0]

    def on_final_point(self):
        pass
