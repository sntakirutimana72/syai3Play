from os import path
from kivy.clock import Clock
from guix.customlayers import CustomLayer
from kivy.uix.widget import Widget
from kivy.core.window import Window
from utils.app_envs import appDataDir
from pyautogui import position as pypos
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.properties import ListProperty, OptionProperty, \
    ObjectProperty, BooleanProperty, StringProperty, NumericProperty


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
        else:
            return super(Dragging, self).on_touch_up(touch)

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


class IconFullPath(object):
    source = StringProperty('')
    icon_name = StringProperty('')

    def on_icon_name(self, interface, value):
        icon_full_relative_path = path.join(appDataDir(), 'data/icons', value)
        if path.isfile(icon_full_relative_path):
            self.source = icon_full_relative_path
        else:
            self.source = ''


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
        self.background_color = [0, 0, 0, 0] if not self.focusBehaved else self.focus_background_color.copy()


class FocusBehaviorHandler(object):
    behaviorFocus = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.register_event_type('on_focusBehavioral')
        super(FocusBehaviorHandler, self).__init__(**kwargs)

    def on_focusBehavioral(self, behavior):
        pass


class ScrollingBehavior(ScrollView):
    bar_color = ListProperty([0, 0, 0, 0])
    bar_inactive_color = ListProperty([0, 0, 0, 0])
    effect_cls = ObjectProperty(OpacityScrollEffect)


class RollingLabel(ScrollingBehavior):
    text = StringProperty('')
    font_size = StringProperty('11sp')
    color = ListProperty([.2, .2, .2, 1])

    autoScroll = BooleanProperty(False)
    '''Indicates whether the property of scrolling is automated or hovered
       :attr: is a :class:`kivy.properties.Boolean` and default to False
       ..Info::`if False it only scrolls on hover else scheduled for every some seconds
    '''
    scrollHandler = None
    '''Object reserved for auto-scrolling re-schedule when is active as to re-initiate auto-scrolling
       every some seconds after the previous scrolling round

       :attr:`python variable` default to None
    '''
    auto_jump_start = None
    ''' invoked when auto-scroll is enabled to jump start before beginning
            to apply restart_time time-frame rule
    '''
    prevent_many_jumps = None
    ''' Once the auto jump start's attempted, this :attr:`prevent_many_jumps` ensures that there
            will be no more jump start instead :attr:`restart_time` is utilized
    '''
    restart_time = NumericProperty(30)

    def __init__(self, **kwargs):
        super(RollingLabel, self).__init__(**kwargs)
        self.animation_1 = None
        self.animation_2 = None

    def on_size(self, *largs):
        root = App.get_running_app().root
        if root.ready is not True:
            return
        self.re_order_schedules()

    def on_children(self, *largs):
        if largs[1]:
            largs[1][0].bind(texture_size=self.on_texture_size)

    def check_viewport_size(self, *largs):
        if not self.size[0]:
            return

        child = self.children[0]
        if child.size[0] > self.size[0]:
            time_frame_const = 35 / 800  # Personal const based on self experience,calculation,observation..
            initial_time = (self.size[0] * time_frame_const)
            duration = (child.size[0] * initial_time / self.size[0])

            if child.hovered and not self.autoScroll:
                self.ready_scroll(child.x, initial_time, duration)
            elif self.autoScroll:
                start_at = 8 if not self.prevent_many_jumps else self.restart_time
                self.auto_jump_start = Clock.schedule_once(
                    lambda x: self.ready_scroll(child.x, initial_time, duration), start_at)

    def ready_scroll(self, *largs):
        if self.auto_jump_start:
            self.auto_jump_start = None
            self.prevent_many_jumps = True

        self.animation_1 = Animation(right=largs[0], d=largs[2])
        self.animation_2 = Animation(x=0, d=largs[1])

        self.animation_1.bind(on_complete=self.animation1_complete)
        self.animation_2.bind(on_complete=self.animation2_complete)
        self.animation_1.start(self.children[0])

    def _restart_scroll(self, *largs):
        if self.animation_1:
            self.animation_1.start(self.children[0])

    def on_texture_size(self, *largs):
        largs[0].width = largs[1][0]
        self.prevent_many_jumps = None
        self.re_order_schedules()

    def re_order_schedules(self):
        self.cancel_schedules()
        self.cancel_animations()

        if self.autoScroll:
            self.check_viewport_size()

    def cancel_schedules(self):
        if self.auto_jump_start:
            self.auto_jump_start.cancel()
            self.auto_jump_start = None

        if self.scrollHandler:
            self.scrollHandler.cancel()
            self.scrollHandler = None

    def cancel_animations(self):
        child = self.children[0]
        if self.animation_1:
            self.animation_1.cancel(child)
        if self.animation_2:
            self.animation_2.cancel(child)

        self.reset_viewport()

    def animation1_complete(self, *largs):
        largs[1].x = self.size[0]
        self.animation_2.start(largs[1])

    def animation2_complete(self, *largs):
        if self.autoScroll:
            self.scrollHandler = Clock.schedule_once(
                self._restart_scroll, self.restart_time)

    def compute_restartTime(self, t_frame=None):
        if t_frame is None:
            self.restart_time = 30
        else:
            ratio = int(t_frame / 50)
            if ratio < 3:
                if t_frame > 30:
                    self.restart_time = t_frame
                return
            if ratio > 10:
                ratio = int(t_frame / (50 * 9))
            self.restart_time = t_frame / ratio

    def on_enter(self):
        if not self.autoScroll:
            self.check_viewport_size()

    def on_leave(self):
        if not self.autoScroll:
            self.cancel_animations()

    def reset_viewport(self):
        self.children[0].x = 0


class BoxLayer(BoxLayout, CustomLayer):
    pass


class GridLayer(GridLayout, CustomLayer):
    pass


class ButtonTemplate(Clicking, CustomLayer, Hovering):
    pass
