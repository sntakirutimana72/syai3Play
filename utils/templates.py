class CustomLayer(object):
    radius = ListProperty([0])
    outline_width = NumericProperty(1)
    outline_color = ListProperty([0, 0, 0, 0])
    background_color = ListProperty([0, 0, 0, 0])
    hover_background_color = ListProperty(None)
    focus_background_color = ListProperty(None)


class IconFullPath(Widget):
    pace = NumericProperty(0)
    radius = ListProperty([0])
    source = StringProperty('')
    icon_name = StringProperty('')
    cover_color = ListProperty([1, 1, 1, 1])

    def on_icon_name(self, widget, value):
        icon_full_relative_path = path.join(appDataDir(), 'images', value)
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
            current_mouse_pos = self.to_local(*pyposition())
            self.parent.x, self.parent.top = [current_mouse_pos[0] - self.dragging_ref_pos[0],
                                              current_mouse_pos[1] - self.dragging_ref_pos[1]]
        elif self.draggable_obj == 'app':
            current_mouse_pos = pyposition()
            Window.left, Window.top = [current_mouse_pos[0] - self.dragging_ref_pos[0],
                                       current_mouse_pos[1] - self.dragging_ref_pos[1]]

    def _regulate_current_pos(self):
        if self.draggable_obj == 'layer':
            current_mouse_pos = self.to_local(*pyposition())
            current_win_left, current_win_top = self.parent.x, self.parent.top
        elif self.draggable_obj == 'app':
            current_mouse_pos = pyposition()
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


class ScrollBehavior(object):
    bar_color = ListProperty([0, 0, 0, 0])
    bar_inactive_color = ListProperty([0, 0, 0, 0])
    effect_cls = ObjectProperty(OpacityScrollEffect)
