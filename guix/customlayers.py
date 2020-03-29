from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, NumericProperty, StringProperty


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


<SquaredLogo>:
    canvas:
        Color:
            rgba: self.cover_color
        Rectangle:
            source: self.source
            pos: self.x + dp(self.pace), self.y + dp(self.pace)
            size: self.width - dp(self.pace * 2), self.height - dp(self.pace * 2)
    size_hint_x: None
    width: self.height
""")


class CustomLayer(Widget):
    border_radius = ListProperty([0])
    border_width = NumericProperty(1)
    border_color = ListProperty([0, 0, 0, 0])
    background_color = ListProperty([0, 0, 0, 0])
    hover_background_color = ListProperty(None)
    focus_background_color = ListProperty(None)


class SquaredLogo(Widget):
    pace = NumericProperty(0)
    source = StringProperty('')
    cover_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(SquaredLogo, self).__init__(**kwargs)
