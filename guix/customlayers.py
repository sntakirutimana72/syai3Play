from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty


Builder.load_string("""
<CustomLayer>:
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            radius: self.border_radius
            pos: self.pos
            size: self.size
        Color:
            rgba: self.border_color
        Line:
            width: 1 if self.border_width is None else self.border_width
            rounded_rectangle: (*self.pos, *self.size, *self.border_radius)
""")


class CustomLayer(Widget):
    border_radius = ListProperty([0])
    border_width = NumericProperty(1)
    border_color = ListProperty([0, 0, 0, 0])
    background_color = ListProperty([0, 0, 0, 0])
    hover_background_color = ListProperty(None)
    focus_background_color = ListProperty(None)
