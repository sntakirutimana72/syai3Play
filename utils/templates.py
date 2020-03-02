from os import path
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.core.window import Window
from utils.app_envs import appDataDir
from pyautogui import position as pypos
from kivy.uix.scrollview import ScrollView
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.properties import ListProperty, NumericProperty, OptionProperty, \
    ObjectProperty, BooleanProperty, StringProperty


class CustomLayer(Widget):
    radius = ListProperty([0])
    outline_width = NumericProperty(1)
    outline_color = ListProperty([0, 0, 0, 0])
    background_color = ListProperty([0, 0, 0, 0])
    hover_background_color = ListProperty(None)
    focus_background_color = ListProperty(None)


class IconFullPath(object):
    pace = NumericProperty(0)
    radius = ListProperty([0])
    source = StringProperty('')
    icon_name = StringProperty('')
    cover_color = ListProperty([1, 1, 1, 1])

    def on_icon_name(self, widget, value):
        icon_full_relative_path = path.join(appDataDir(), 'icons', value)
        if path.isfile(icon_full_relative_path):
            self.source = icon_full_relative_path
        else:
            self.source = ''


class Hovering(object):
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.register_event_type('on_hover')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_hover)
        super(Hovering, self).__init__(**kwargs)

    def on_mouse_hover(self, *largs):
        if not self.get_root_window():
            return
        obj_pos = largs[1]
        mouse_entered = self.collide_point(*self.to_parent(*obj_pos))

        if self.hovered == mouse_entered:
            return
        self.hovered = mouse_entered
        self.dispatch('on_hover' if mouse_entered else 'on_leave')

    def on_hover(self):
        pass

    def on_leave(self):
        pass


class Dragging(Widget):
    draggable_obj = OptionProperty('layer', options=['layer', 'app', 'none'])

    def __init__(self, **kwargs):
        self.register_event_type('on_drag_window') if self.draggable_obj != 'none' else ''
        super(Dragging, self).__init__(**kwargs)
        self.dragging_ref_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            ctrl_widget = self.ids.get('header_controls')
            if ctrl_widget and ctrl_widget.collide_point(*touch.pos):
                return super(Dragging, self).on_touch_down(touch)
            if self.draggable_obj == 'none':
                return True

            touch.grab(self)
            Window.grab_mouse()
            self._regulate_current_pos()
            return True
        return super(Dragging, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current == self:
            self.dispatch('on_drag_window')

    def on_touch_up(self, touch):
        if touch.grab_current == self:
            touch.ungrab(self)
            Window.ungrab_mouse()

    def on_drag_window(self):
        if self.draggable_obj == 'layer':
            current_mouse_pos = self.to_local(*pypos())
            self.parent.x, self.parent.top = [current_mouse_pos[0] - self.dragging_ref_pos[0],
                                              current_mouse_pos[1] - self.dragging_ref_pos[1]]
        elif self.draggable_obj == 'app':
            current_mouse_pos = pypos()
            Window.left, Window.top = [current_mouse_pos[0] - self.dragging_ref_pos[0],
                                       current_mouse_pos[1] - self.dragging_ref_pos[1]]

    def _regulate_current_pos(self):
        if self.draggable_obj == 'layer':
            current_mouse_pos = self.to_local(*pypos())
            current_win_left, current_win_top = self.parent.x, self.parent.top
        elif self.draggable_obj == 'app':
            current_mouse_pos = pypos()
            current_win_left, current_win_top = Window.left, Window.top

        self.dragging_ref_pos = [current_mouse_pos[0] - current_win_left,
                                 current_mouse_pos[1] - current_win_top]


class Clicking(Widget):

    def __init__(self, **kwargs):
        self.register_event_type('on_press')
        self.register_event_type('on_release')
        super(Clicking, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_press')
            return True
        return super(Clicking, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.dispatch('on_release')
            return True
        return super(Clicking, self).on_touch_up(touch)

    def on_press(self):
        pass

    def on_release(self):
        pass


class FocusBehaviorHandler(object):
    behaviorFocus = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.register_event_type('on_focusBehavioral')
        super(FocusBehaviorHandler, self).__init__(**kwargs)

    def on_focusBehavioral(self, behavior):
        pass


class FocusBehavior(object):
    focusBehaved = BooleanProperty(False)

    def on_focusBehaved(self, widget, behaved):
        if not behaved:
            self.background_color = [0, 0, 0, 0]
        elif behaved and not self.hovered:
            self.background_color = self.focus_background_color.copy()

    def on_release(self):
        if not self.focusBehaved:
            self.focusBehaved = True

    def on_hover(self):
        self.background_color = self.hover_background_color.copy()

    def on_leave(self):
        self.background_color = [0, 0, 0, 0] \
            if not self.focusBehaved \
            else self.focus_background_color.copy()


class ScrollBehavior(ScrollView):
    bar_color = ListProperty([0, 0, 0, 0])
    bar_inactive_color = ListProperty([0, 0, 0, 0])
    effect_cls = ObjectProperty(OpacityScrollEffect)


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