from kivy.config import Config
Config.set('graphics', 'borderless', 1)

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.animation import Animation
# from kivy.core.audio import SoundLoader
from kivy.uix.scrollview import ScrollView
from kivy.effects.opacityscroll import OpacityScrollEffect
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.textinput import TextInput
from kivy.uix.accordion import AccordionItem
from kivy.properties import ListProperty, OptionProperty, \
  BooleanProperty, ObjectProperty, NumericProperty, StringProperty

from configparser import ConfigParser
from os.path import basename, join
# from threading import Thread, Lock
import json, pyautogui as pyauto
import re, os, asyncio, sys

SETTINGS = None


async def addTo_list(root, filet):
  icon = join('./Icons', filet[-3:].lower() + '.png')
  fil = PlaylistItem(me=basename(
    filet), source=icon, on_down=root._playItem_pressedOnce_)
  root.ids.nowList.add_widget(fil)


def add_newDroppedTo_list(root):
  files_range = range(len(root._playList))
  for i in files_range:
    addTo_list(root, root._playList.pop())
  root.show_loading_status()  # Removing file dropping status


def startUp_window_size():
  window = json.loads(SETTINGS.get('window', 'window'))
  Window.size = window.get('window-size')


def startUp_window_pos():
  window = json.loads(SETTINGS.get('window', 'window'))
  Window.left, Window.top = window.get('window-pos')


def load_setting_onStartUp():
  global SETTINGS
  SETTINGS = ConfigParser()
  SETTINGS.read('./settings.ini')

  Window.minimum_width = 450
  Window.minimum_height = 68

  startUp_window_size()


load_setting_onStartUp()

Builder.load_string('''
<MainRoot>:
    orientation: 'vertical'
    normal: root.getProperty('custom body bkg-color')
    outl_w: root.getProperty('custom body border-width')
    outl_clr: root.getProperty('custom body border-color')

    HeadBar:
        canvas:
            Color:
                rgba: [0, 1, 1, .01]
            SmoothLine:
                width: 2
                points: (*self.pos, self.right, self.y)
        rows: 1
        size_hint_y: None
        height: dp(30)
        normal: root.getProperty('custom title bkg-color')
        GridLayout:
            minimum_width: dp(120)
            padding: 6
            rows: 1

            # Logo-Image
            CustomButton:
                hoverClr: ()
                size_hint_x: None
                width: self.height
                source: root.getProperty("custom title logo-image")

            # Application-Name
            Label:
                shorten: True
                valign: "middle"
                text: 'SYAI3Play'
                text_size: self.size
                font_size: min(*self.size) // 2 + 1 \
                    if not (min(*self.size) // 2) % 2 \
                    else min(*self.size) // 2 + 2
                font_name: root.getProperty("custom title font-name")
                color: root.getProperty("custom title font-color")
                
        # Player PosterOffice and must be of 2 children widgets
        BoxLayout:
            padding: (20, 6)
            spacing: '5sp'
            maximum_width: dp(360)
            
            AutoRollLabel:
            CustomButton:
                size_hint_x: None
                width: dp(self.height + 2)
                source: './Icons/more.png'
                on_down: root._revealMoreOptions()

        # Window function buttons
        GridLayer:
            size_hint_x: None
            width: dp(72)
            padding: 7
            spacing: 5
            rows: 1
            WindowCtrls:
                on_down: self.do_resize()
                source: './Icons/green.png'
            WindowCtrls:
                on_down: self.do_minimize()
                source: './Icons/yellow.png'
            WindowCtrls:
                on_down: self.do_terminate()
                source: './Icons/red.png'

    # body-div
    ScreenManager:
        id: disp_manager  
        PlayScreen:
            name: 'main'
            id: main_screen
            
            # main child of the screen widget
            BoxLayout:
                id: msc_cont
                  
                # right nav container  
                BoxLayout:
                    orientation: 'vertical'
                    # playlist nav
                    FloatLayout:
                        size_hint_y: None
                        height: dp(root.height - 128) if root.height > 128 else 0
                        CustomButton:
                            normal: (0, 0, 0, 0) if self.size[1] < 10 else (.4, .4, .6, 1)
                            pos: self.parent.pos
                            pos_hint: {'center_y': .5, 'center_x': .5}
                            source: './Icons/thumbnail.png'
                            hoverClr: ()
                            size_hint: (None, None)
                            height: dp(150) \
                              if self.parent.height > 150 \
                              else dp(self.parent.height / 1.2)
                            width: self.height
                            radius: [0]
                            
                    # player control view
                    BoxLayout:
                        orientation: 'vertical'
                        # controls-row1
                        BoxLayer:
                            id: row_1
                            normal: (1, 0, 1, .02)
                            size_hint_y: None
                            height: dp(38)
                            spacing: '4sp'
                            padding: (15, 8)
                            
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/preview.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/stop.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/play.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/rewind.png'
                                
                            # Volume control
                            FloatLayout:
                                id: vol_cont
                                padding: (5, 0)
                                HrzProgressBar:
                                    pos: self.parent.pos
                                    pos_hint: {'center_y': .5} 
                                    size_hint_y: None
                                    height: dp(4)
                                
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/wind.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/shuffle-off.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/repeat-off.png'
                            CustomButton:
                                size_hint_x: None
                                width: dp(self.height + 1)
                                source: './Icons/next.png'
                                
                        # controls-row2
                        BoxLayout:
                            id: row_2
                            orientation: 'vertical'
                            size_hint_y: None
                            height: dp(60)
                            spacing: '6sp'
                            padding: (15, 5)
                            
                            BoxLayout:
                                spacing: '5sp'
                                
                                # Volume Level
                                StatusDisplayLabel:
                                    display_type: 'vol'
                                    width: dp(65)
                                    textVal: '100.0'
                                # Media Format
                                StatusDisplayLabel:
                                    display_type: 'format'
                                    width: dp(75)
                                    textVal: 'mp3'
                                # Media State
                                StatusDisplayLabel:
                                    display_type: 'state'
                                    width: dp(75)
                                    textVal: 'off'
                                # Media Name
                                AutoRollLabel:
                                    text: 'media file sample.mp3'     
                            BoxLayout:
                                spacing: '12sp'
                                
                                # Elapsed Time
                                MediaTimeCounter:
                                    text: 'Elapsed Time'
                                FloatLayout:
                                    id: progress_cont
                                    HrzProgressBar:
                                        handler_normal: [0, .1, 0, 1]
                                        level_normal: [1, 1, 0, .2]
                                        pos: self.parent.pos
                                        pos_hint: {'center_y': .5} 
                                        size_hint_y: None
                                        height: dp(4)
                                # Estimated Duration
                                MediaTimeCounter:
                                    text: 'Estimated Time'
                            Label:
                                size_hint_y: None
                                height: dp(10)

<AutoRollLabel>:
    HoverableLabel:
        text: root.text
        valign: 'middle'
        halign: 'center'
        color: root.color
        size_hint_x: None
        # font_name: 'FreeMono'
        font_size: root.font_size
        text_size: (None, self.size[1])
        width: self.texture_size[0]
        on_enter: root.on_enter()
        on_leave: root.on_leave()

<WindowCtrls>:
    canvas:
        Color:
            rgba: self.normal 
        Ellipse:
            pos: self.pos
            size: self.size
            source: self.source
            
<MoreOptions>:
    normal: (.12, .12, .15, 1)
    pos_hint: {'top': 1}
    size_hint_y: None
    height: dp(38)
    
    BoxLayer:
        normal: (1, .3, 1, .02)
        padding: ((self.width - 390) * .5, 5)
        spacing: '5sp'
        
        # SETTINGS
        CustomButton:
            normal: (1, .8, 1, .07)
            size_hint_x: None
            text: 'settings'
            width: dp(60)
        
        # SearchBox
        BoxLayer:
            normal: (.15, .15, .15, 1)
            radius: [4]
            InputField:
                text: 'Find and play'
                font_name: 'FreeMono'
            CustomButton:
                size_hint_x: None
                width: self.height
                h_normal: (1, 0, 0, .1)
                radius: [0, 4, 4, 0]
                source: './Icons/search.png'
                
        # DOCK
        CustomButton:
            on_down: root.root.on_miniDockSwitch()
            normal: (1, .8, 1, .07)
            size_hint_x: None
            width: dp(50)
            text: 'dock'
                        
<HrzProgressBar>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius 

        Color:
            rgba: self.level_normal
        RoundedRectangle:
            pos: self.pos
            size: (self.progressLevel, self.size[1])
            radius: self.radius

        Color:
            rgba: self.handler_normal
        Ellipse:
            pos: (self.pos[0] + self.progressLevel - 7, self.pos[1] - (14 - self.height) / 2)
            size: (14, 14)
            source: ""
            
    canvas:
        Color:
            rgba: self.handlerOuter_normal
        Line:
            width: 1.1
            circle: (self.pos[0] + self.progressLevel, self.pos[1] + self.size[1] * .5, 7)

<MediaTimeCounter>:
    size_hint_x: None
    text_size: (None, self.size[1])
    width: self.texture_size[0]
    
<StatusDisplayLabel>:
    size_hint_x: None
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            radius: self.radius
            pos: self.pos
            size: self.size
            
<LeftNavMenu>:
    size_hint_x: None
    splitter: splitter.__self__
    ScrollInactiveBar:
        BoxLayout:
            padding: '4sp'
            size_hint_y: None
            height: max(self.minimum_height, dp(250))
            Accordion:
                id: left_nav
                orientation: 'vertical'
                
                LeftNavElement:
                    title: 'Library'
                    background_normal: './Icons/library.png'
                    GridLayout:
                        cols: 1
                        size_hint_y: None
                        height: max(self.minimum_height, dp(150))
                LeftNavElement:
                    title: 'Streaming'
                    background_normal: './Icons/streaming.png'
                    GridLayout:
                        cols: 1
                        size_hint_y: None
                        height: max(self.minimum_height, dp(150))
                LeftNavElement:
                    title: 'Playlists'
                    background_normal: './Icons/playlist.png'
                    GridLayout:
                        cols: 1
                        size_hint_y: None
                        height: max(self.minimum_height, dp(150))
    CustomButton:
        id: splitter
        radius: [0]
        size_hint_x: None
        width: root.strip_size
        h_normal: root.strip_hoverClr
        hoverClr: root.strip_hoverClr
        source: root.strip_backgroundImg
        normal: root.strip_backgroundClr

<CustomButton>:
    canvas.before:
        Color:
            rgba: self.h_normal
        RoundedRectangle:
            radius: self.radius
            pos: self.pos
            size: self.size
            
        Color:
            rgba: self.normal
        Rectangle:
            source: self.source
            pos: (self.pos[0] + 2, self.pos[1] + 2)
            size: (self.size[0] - 4, self.size[1] - 4)

<GridLayer>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius

<BoxLayer>:
    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: self.radius
    canvas:
        Color:
            rgba: self.outl_clr
        Line:
            width: self.outl_w
            rounded_rectangle: (*self.pos, *self.size, *self.outl_r)

<Loading>:
    canvas:
        Color:
            rgba: (.1, .1, .1, .1)
        Line:
            width: 2
            ellipse: (self.center_x - self.size[1] / 2, \
                    self.pos[1], self.size[1], self.size[1])

        PushMatrix
        Rotate:
            origin: self.center
            angle: self.angle
            axis: (0, 0, 1)
        Color:
            rgba: (1, 1, 1, .2)
        Line:
            width: 1.01
            ellipse: (self.center_x - self.size[1] / 2, \
                      self.pos[1], self.size[1], self.size[1], 0, 95)
        PopMatrix

<PlaylistItem>:
    size_hint_y: None
    height: dp(24)
    canvas:
        Color:
            rgb: (1, 1, 1)
        RoundedRectangle:
            radius: [2]
            source: self.source
            pos: (self.pos[0] + 2, self.pos[1] + 2)
            size: (self.height - 4, self.height - 4)

    canvas.before:
        Color:
            rgba: self.normal
        RoundedRectangle:
            radius: [2]
            pos: self.pos
            size: self.size
    Label:
        shorten: True
        text: root.text
        valign: 'middle'
        font_size: '12sp'
        size_hint_x: None
        text_size: self.size
        color: (1, .6, .8, 1)
        width: root.size[0] - 30
        font_name: "Trebuchet_MS_Italic"
        pos_hint: {'right': 1, 'center_y': .5}
''')


class Loading(Label):
  angle = NumericProperty(0)
  name = StringProperty(None)

  def __init__(self, **kwargs):
    super(Loading, self).__init__(**kwargs)
    Clock.schedule_interval(self._update_angle, 0)

  def _update_angle(self, dt):
    self.angle -= 9

  def on_parent(self, *largs):
    if not largs[1]:
      Clock.unschedule(self._update_angle)


class MediaTimeCounter(Label):
  '''
  :class:inherits from :class:`kivy.uix.label`
  ..value::`Created to display elapsed and estimated time
      while the player is functioning
  '''
  time_stamp = NumericProperty(None)
  '''A container for time stamp to rationalize
     :attr: is a :class:`kivy.properties` and default to None
     
     ..Warning::`Only decimal or real number are accepted
  '''
  font_name = 'FreeMonoBold'
  font_size = 11

  def on_time_stamp(self, *largs):
    if not largs[1]:
      rationTime = ''
    else:
      hours = largs[1] // 3600
      minutes = (largs[1] % 3600) // 60
      seconds = (largs[1] % 3600) % 60

      if hours == 0.:
        rationTime = '{:02.0f}:{:02.0f}'.format(minutes, seconds)
      else:
        rationTime = '{:.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)
    self.text = rationTime


class StatusDisplayLabel(Label):
  normal = ListProperty([1, 1, 0, .02])
  radius = ListProperty([2])

  display_type = OptionProperty(
    'none', options=['none', 'vol', 'format', 'state'])
  '''Remarks the such type should the assign text value presents
  
    :attr: is a :class:`kivy.properties` and default to `none`
    ..Warning:: ony accepts of the its options values
  '''
  textVal = StringProperty('')
  '''Temporal container for text value for reformatting with its type

      :attr: is a :class:`kivy.properties` and default to ''
    '''
  font_name = 'FreeMonoBold'
  color = [0, 1, 1, 1]
  font_size = 10
  markup = True

  def on_textVal(self, *largs):
    if not largs[1]:
      return
    if self.display_type == 'vol':
      val = 'vol ' + largs[1] + '%'
    elif self.display_type == 'format':
      val = 'format: ' + largs[1]
    elif self.display_type == 'state':
      val = 'status: ' + largs[1]

    self.text = val
    self.textVal = ''


class Hoverable(object):
  hovered = BooleanProperty(False)

  def __init__(self, **kwargs):
    self.register_event_type('on_enter')
    self.register_event_type('on_leave')
    Window.bind(mouse_pos=self.on_mouse_pos)
    super(Hoverable, self).__init__(**kwargs)

  def on_mouse_pos(self, *largs):
    if not self.get_root_window():
      return

    pos = largs[1]
    inside = self.collide_point(*self.to_widget(*pos))
    if self.hovered == inside:
      return
    self.hovered = inside

    if inside:
      self.dispatch('on_enter')
    else:
      self.dispatch('on_leave')

  def on_enter(self):
    pass

  def on_leave(self):
    pass


class HoverableLabel(Label, Hoverable):
  font_size = NumericProperty('11sp')
  color = ListProperty([.4, .4, .3, 1])


class ScrollInactiveBar(ScrollView):
  bar_color = ListProperty([0, 0, 0, 0])
  bar_inactive_color = ListProperty([0, 0, 0, 0])
  effect_cls = ObjectProperty(OpacityScrollEffect)


class GridLayer(GridLayout):
  radius = ListProperty([0])
  normal = ListProperty([0, 0, 0, 0])


class BoxLayer(BoxLayout):
  radius = ListProperty([0])
  outl_r = ListProperty([0])
  outl_w = NumericProperty(1)
  normal = ListProperty([0, 0, 0, 0])
  outl_clr = ListProperty([0, 0, 0, 0])


class LeftNavMenu(BoxLayout):
  root = ObjectProperty(None)
  '''A reference to root widget and reserved for generating mode switching
       between minimal and dock view events
    :attr: is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''
  strip_size = NumericProperty(5)
  '''width size value for the splitter
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 6
  '''
  strip_backgroundImg = StringProperty('')
  '''splitter background image if preferred
    :attr: is a :class:`~kivy.properties.StringProperty` and default to ''
  '''
  strip_backgroundClr = ListProperty([1, 1, 1, .01])
  '''splitter background color
    :attr: is a :class:`~kivy.properties.ListProperty` and default to [.8, .8, 1, .05]
  '''
  strip_hoverClr = ListProperty([.4, 1, 1, .01])
  '''splitter hover background color
    :attr: is a :class:`~kivy.properties.ListProperty` and default to [0, 1, 1, .01]
  '''
  min_size = NumericProperty(200)
  '''self size that the splitter cannot go pass while decreasing size and also
      it's the default self size
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 200
  '''
  max_size = NumericProperty(200)
  '''self size that the splitter cannot go pass while increasing size
    :attr: is a :class:`~kivy.properties.NumericProperty` and default to 200
  '''
  splitter = ObjectProperty(None)
  '''a splitter widget
    :attr: is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''

  def __init__(self, **kwargs):
    self.register_event_type('on_split_size')
    super(LeftNavMenu, self).__init__(**kwargs)
    self.width = self.min_size
    if self.min_size > self.max_size:
      self.min_size = self.max_size

  def on_touch_down(self, touch):
    if self.splitter.collide_point(*touch.pos):
      touch.grab(self)
      self.dispatch('on_split_size', touch.pos[0])
      return True
    return super(LeftNavMenu, self).on_touch_down(touch)

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self.dispatch('on_split_size', touch.pos[0])
    return True

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      touch.ungrab(self)
    return True

  def on_split_size(self, pos_x):
    new_width = pos_x - self.pos[0]
    if self.min_size <= new_width <= self.max_size:
      self.width = new_width

  def on_max_size(self, *largs):
    self.normalize_max_size()

  def on_parent(self, *largs):
    if not largs[1]:
      self.width = self.min_size

  def normalize_max_size(self):
    if self.width > self.max_size:
      self.width = self.max_size


class LeftNavElement(AccordionItem):
  title = 'Element of left navigation'


class InputField(TextInput):
  write_tab = BooleanProperty(False)
  font_size = NumericProperty('12sp')
  multiline = BooleanProperty(False)
  cursor_color = ListProperty([1, 1, .7, 1])
  background_color = ListProperty([0, 0, 0, 0])
  foreground_color = ListProperty([.5, .5, .5, 1])


class HeadBar(GridLayer):

  def __init__(self, **kwargs):
    self.register_event_type('on_drag_window')
    super(HeadBar, self).__init__(**kwargs)

  def on_touch_down(self, touch):
    if not (not (self.children[0].collide_point(
        *touch.pos) or self.children[1].children[0].collide_point(
      *touch.pos)) and self.collide_point(*touch.pos)):
      return super(HeadBar, self).on_touch_down(touch)

    touch.grab(self)
    pos = pyauto.position()
    left, top = Window.left, Window.top
    self.drag_pos = [pos[0] - left, pos[1] - top]
    return True

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self.dispatch('on_drag_window')

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      touch.ungrab(self)

  def on_drag_window(self):
    pos = pyauto.position()
    Window.left, Window.top = (
      pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])


class HrzProgressBar(HoverableLabel):
  radius = ListProperty([0])
  normal = ListProperty([.2, .2, .2, .3])
  level_normal = ListProperty([.8, .1, 0, .2])
  handler_normal = ListProperty([.1, 0, 0, 1])
  handlerOuter_normal = ListProperty([.2, .22, .2, 1])

  progressLevel = NumericProperty(0.)
  '''Track bar level in percentage 0.0%
    :attr: is a :class:`kivy.properties.NumericProperty` and default
      to 0.0
    ..Warnings:: it takes only decimal or real number not percentile
  '''
  visible = OptionProperty('none', options=['none', 'off', 'in', 'out'])
  '''Adjuster or handler clocking capability
    :attr: is a :class:`kivy.properties.OptionProperty` and default
      to None
      
    ..Warning:: it takes only one among ['off', 'in', 'out', 'none']
    
    :value::`off`: means the handler is invisible
    :value::`in or out`: means the handler can switch between visible and invisible modes
    
  '''
  bar_active = BooleanProperty(True)
  '''Disables & Enables the interactivity of the handler
  
    :attr: is a :class:`kivy.properties.Boolean` and default to True
    :False::`disables`
    :True::`Enables`
  '''
  autoSwitchMode = None
  '''Automates the visibility mode switching when :attr::visible::`is enabled`
    :attr: is a :object:`python const` and default to None 
  '''
  widthConst = None
  '''previous width container and to be used when auto resize triggered
      in order to re-normalize progressLevel    
    :attr: is a :object:`python const` and default to None 
  '''

  def on_size(self, *largs):
    if not self.progressLevel:
      self.widthConst = largs[1][0]
      return
    self.re_normalize_level()

  def on_enter(self):
    if self.visible in ('none', "off"):
      return
    self.autoSwitchMode.cancel()
    self._changeVisibility()

  def _changeVisibility(self, *largs):
    self.visible = "out" if largs else "in"

  def on_leave(self):
    if self.visible in ('none', "off"):
      return
    self.autoSwitchMode()

  def on_visible(self, *largs):
    if largs[1] in ("off", "out"):
      self.handler_normal[-1] = self.handlerOuter_normal[-1] = 0
    elif largs[1] == "in":
      if self.autoSwitchMode is None:
        self.autoSwitchMode = Clock.schedule_once(self._changeVisibility, 5)
      else:
        self.handler_normal[-1] = self.handlerOuter_normal[-1] = 1

  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      if self.bar_active:
        touch.grab(self)
        self._normalize_move_(touch.pos[0])
      return True
    return super(HrzProgressBar, self).on_touch_down(touch)

  def on_touch_move(self, touch):
    if touch.grab_current == self:
      self._normalize_move_(touch.pos[0])

  def on_touch_up(self, touch):
    if touch.grab_current == self:
      touch.ungrab(self)

  def _normalize_move_(self, pos_x):
    x = pos_x - self.x
    if x < 0:
      x = 0
    elif x > self.width:
      x = self.width
    self.progressLevel = x

  def re_normalize_level(self):
    self.progressLevel *= self.size[0] / self.widthConst
    self.widthConst = self.size[0]


class AutoRollLabel(ScrollInactiveBar):
  text = StringProperty('playlist name testing UI')
  color = ListProperty([.2, .2, .2, 1])
  font_size = StringProperty('11sp')

  autoScroll = BooleanProperty(False)
  '''Indicates whether the property of scrolling is automated or hovered
     :attr: is a :class:`kivy.properties.Boolean` and default to False
     ..Info::`if False it only scrolls on hover else scheduled for every some seconds
  '''
  scrollHandler = None
  '''Object reserved for auto-scrolling when is active as to re-initiate auto-scrolling
     every some seconds after the previous scrolling round
     
     :attr:`python variable` default to None
  '''

  def __init__(self, **kwargs):
    super(AutoRollLabel, self).__init__(**kwargs)
    self.animation_1 = None
    self.animation_2 = None

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
      self.ready_scroll(child.x, initial_time, duration)

  def ready_scroll(self, *largs):
    self.animation_1 = Animation(right=largs[0], d=largs[2])
    self.animation_2 = Animation(x=0, d=largs[1])

    self.animation_1.bind(on_complete=self.animation1_complete)
    self.animation_2.bind(on_complete=self.animation2_complete)
    self.animation_1.start(self.children[0])

  def _restart_scroll(self, *largs):
    if self.animation_1:
      self.animation_1.start(self.children[0])

  def on_texture_size(self, *largs):
    if self.scrollHandler:
      self.scrollHandler.cancel()
      self.scrollHandler = None
    self.cancel_animations()

    if self.autoScroll:
      self.check_viewport_size()

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
      self.scrollHandler = Clock.schedule_once(self._restart_scroll, 10)

  def on_enter(self):
    if not self.autoScroll:
      self.check_viewport_size()

  def on_leave(self):
    if not self.autoScroll:
      self.cancel_animations()

  def reset_viewport(self):
    self.children[0].x = 0


class CommonLabelButton(HoverableLabel):
  hoverClr = ListProperty([1, .8, 1, .1])

  def __init__(self, **kwargs):
    self.register_event_type('on_up')
    self.register_event_type('on_down')
    super(CommonLabelButton, self).__init__(**kwargs)

  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      self.dispatch('on_down')
      return True
    return super(CommonLabelButton, self).on_touch_down(touch)

  def on_touch_up(self, touch):
    if self.collide_point(*touch.pos):
      self.dispatch('on_up')
      return True
    return super(CommonLabelButton, self).on_touch_up(touch)

  def on_up(self):
    pass

  def on_down(self):
    pass


class CustomButton(CommonLabelButton):
  h_normal = ListProperty([0, 0, 0, 0])
  normal = ListProperty([1, 1, 1, 1])
  radius = ListProperty([2])
  source = StringProperty("")

  def on_enter(self):
    self.exchange_color()

  def on_leave(self):
    self.exchange_color()

  def exchange_color(self):
    if not self.hoverClr:
      return

    n, h = self.h_normal.copy(), self.hoverClr.copy()
    self.h_normal, self.hoverClr = h, n


class WindowCtrls(CommonLabelButton):
  normal = ListProperty([1, 1, 1, .5])
  source = StringProperty('')

  def on_enter(self):
    self.normal[-1] = 1

  def on_leave(self):
    self.normal[-1] = .5

  def do_minimize(self):
    Window.minimize()

  def do_resize(self):
    app = App.get_running_app()
    app.root.do_resize()

  def do_terminate(self):
    #  An event for terminating the whole application processes pool
    App.stop(App.get_running_app())


class MoreOptions(BoxLayer):
  root = ObjectProperty(None, allownone=True)
  '''A reference to root widget and reserved for generating mode switching
       between minimal and dock view events
    :attr: is a :class:`~kivy.properties.ObjectProperty` and default to None
  '''

  def on_touch_down(self, touch):
    if not self.collide_point(*touch.pos):
      if self.parent:
        self.parent.remove_widget(self)
        self.root = None
    return super(MoreOptions, self).on_touch_down(touch)


class PlaylistItem(FloatLayout, Hoverable):
  normal = ListProperty([.16, .16, .16, 1])
  hoverClr = ListProperty([0, .3, 0, 1])
  source = StringProperty("")
  text = StringProperty("")
  me = StringProperty(None)

  choice = True
  _pressed_ = None

  def __init__(self, **kwargs):
    self.register_event_type('on_down')
    self.register_event_type('on_double')

    super(PlaylistItem, self).__init__(**kwargs)
    PlaylistItem.choice = not PlaylistItem.choice
    self.normal[-1] = 1 if PlaylistItem.choice else 0
    self.text = basename(self.me)

  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      if touch.is_double_tap:
        self.dispatch('on_double')
      else:
        self.dispatch('on_down')
      return True
    return super(PlaylistItem, self).on_touch_down(touch)

  def on_double(self):
    pass

  def on_down(self):
    pass

  def on_enter(self):
    self.exchange_color()

  def on_leave(self):
    self.exchange_color()

  def exchange_color(self):
    if not self.hoverClr or self._pressed_:
      return

    n, h = self.normal.copy(), self.hoverClr.copy()
    self.normal, self.hoverClr = h, n


class MainRoot(BoxLayer):
  ready = None
  viewMode = OptionProperty('mini', options=['mini', 'dock', 'full'])
  '''Used to set a proper view mode with relation its correspondent size
  
    :attr: is a :class:`kivy.properties` and default to `mini`
    ..Warning:: Only accepts of the its options values
  '''
  strippedViews = None
  '''Temporal container for the stripped views to be reused when needed

    :attr: is a :class:`<dict>` and default to None
  '''
  resizeLock = True
  '''Temporal permission lock when switching modes and changing window size
        `It prevents window auto reshaping on resize while switching mode manually

    :attr: is a :class:`<bool>` and default to None
  '''
  temp_pos = None
  '''Temporal position when changing window size manually

    :attr: is a :class:`<list>` and default to None
  '''

  def __init__(self, **kwargs):
    super(MainRoot, self).__init__(**kwargs)
    self.ready = Clock.schedule_interval(self._getReady_, .1)

  def on_size(self, *largs):
    if self.resizeLock is None:
      self.update_left_nav_size(largs[1][0])

  def update_left_nav_size(self, width):
    if len(self.ids.msc_cont.children) > 1:
      left_nav = self.ids.msc_cont.children[1]
      left_nav.max_size = width - 450

  def do_resize(self):
    # preventing window from making auto view switching on resize
    self.resizeLock = True

    if self.viewMode == 'full':
      x, total_x = self.width, pyauto.size()
      ratio = x / total_x[0]
      if ratio >= .95:
        size = (650, total_x[1] * .65)
        pos = self.temp_pos
        self.temp_pos = None
      else:
        size = total_x
        pos = [0, 0]
        self.temp_pos = Window.left, Window.top

      Window.size = size
      Window.left, Window.top = pos
    else:
      self.switch_to_full_view()

    # re-enabling window auto view switching on resize
    self.resizeLock = None

  def playlist_fromCLI(self, *largs):
    print(largs)  # Capture all inputs from command line on startup

  def _getReady_(self, *largs):
    if self.ids:
      # window main GUIs'ready
      self.ready.cancel()
      self.ready = True
      startUp_window_pos()
      self.resizeLock = None
      # self.enable_drop_file()

  def getProperty(self, prop_name):
    try:
      property_parts = prop_name.split(' ')
      section = property_parts[0]
      prop = property_parts[1]
      key = property_parts[2]
      property = json.loads(SETTINGS.get(section, prop))
      return property.get(key)
    except Exception as error:
      Logger.warning("MAIN-PropertyFetch: %s" % error)

  def prep_stripped_container(self):
    if self.strippedViews is None:
      self.strippedViews = {}

  def switch_to_minimal_view(self):
    if self.viewMode == 'full':
      pass

    # retrieving row_2 view from store
    row_2 = self.strippedViews['row_2']['self']
    # stripping progress container from its current parent and re-assign it
    progress_cont = self.ids.row_1.children[0]
    progress_cont.parent.remove_widget(progress_cont)
    row_2.children[1].add_widget(progress_cont, 1)
    # restoring row_2 to its original position and parent
    row2_parent = self.strippedViews['row_2']['parent']
    row2_parent.add_widget(row_2)
    # Resizing Window after stripping
    Window.size = [450, 128]
    # deleting row_2 contents from store
    del self.strippedViews['row_2']
    # resetting view mode to minimal view mode
    self.viewMode = 'mini'

  def switch_to_dock_view(self):
    self.prep_stripped_container()

    if self.viewMode == 'full':
      # stripping left-nav from its parent
      left_nav = self.ids.msc_cont.children[1]
      left_nav.parent.remove_widget(left_nav)
      # storing left-nav for later re-use
      self.strippedViews['left-nav'] = left_nav

    # stripping row_2 view from its parent
    row_2 = self.ids.row_2
    row2_parent = row_2.parent
    row2_parent.remove_widget(row_2)
    # Resizing Window after stripping
    Window.size = [450, 68]
    # stripping progress container view from its parent
    progress_cont = row_2.children[1].children[1]
    progress_cont.parent.remove_widget(progress_cont)
    # storing stripped row_2 view
    self.strippedViews['row_2'] = {'self': row_2, 'parent': row2_parent}
    # volume container shrinking and misplacing
    self.ids.vol_cont.maximum_width = 90
    # adding progress container to row_1
    self.ids.row_1.add_widget(progress_cont)
    # resetting view mode to dock mode
    self.viewMode = 'dock'

  def switch_to_full_view(self):
    self.resizeLock = True

    if self.viewMode == 'dock':
      # switching to minimal view mode first if required
      self.switch_to_minimal_view()

    self.prep_stripped_container()
    # retrieving left-nav if store earlier
    left_nav = self.strippedViews.get('left-nav')
    # checking if the left-nav was once already created
    if not left_nav:
      # creating the left-nav for the first time if necessary
      left_nav = LeftNavMenu(root=self)
    else:
      # deleting the left-nav if found in store
      del self.strippedViews['left-nav']
    # assigning left-nav to a parent
    self.ids.msc_cont.add_widget(left_nav, 1)
    # resizing window to the minimal size of full mode view
    Window.size = [650, 250]
    # setting view mode indicator to full mode
    self.viewMode = 'full'
    # re-enabling auto mode view switching on window resize
    self.resizeLock = None

  def _revealMoreOptions(self):
    current_s = self.ids.disp_manager.current_screen
    current_s.add_widget(MoreOptions(root=self))

  def on_miniDockSwitch(self):
    self.resizeLock = True

    if self.viewMode == 'dock':
      self.switch_to_minimal_view()
    else:
      self.switch_to_dock_view()

    self.resizeLock = None

  def stabilize_progress_bars(self):
    self.ids.vol_cont.children[0].re_normalize_level()
    self.ids.progress_cont.children[0].re_normalize_level()


class PlayScreen(Screen):
  # app main screen
  pass


class MainApp(App):
  title = 'SYAI3Play'
  use_kivy_settings = False

  def build(self):
    return _mainRoot_

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
      self.config.read('./settings.ini')
      self.config["window"]["window"] = json.dumps({
        'window-size': [450, 128],
        'window-pos': [Window.left, Window.top]
      })
      self.config.write()
    except:
      pass

    sys.exit(0)


if __name__ == '__main__':
  _mainRoot_ = MainRoot()
  if len(sys.argv) > 1:
    _mainRoot_.playlist_fromCLI(sys.argv[1:])

  MainApp().run()


# def on_drop_file(self, *largs):
  #   if self.__autoplay is None:
  #     Clock.unschedule(self._check_StartUp_autoPlay_)
  #     Clock.schedule_once(self._check_StartUp_autoPlay_, 2.6)
  #
  #   if self.__showLoader is None:
  #     self.show_loading_status()
  #
  #   filet = largs[1].decode('utf-8')
  #   audioFormatRegex = re.compile(r'mp3|wav|ogg|m4a|mp2', re.I)
  #   if audioFormatRegex.search(filet[-3:]) and (filet not in self._playList):
  #     self._playList.append(filet)
  #
  # def enable_drop_file(self):
  #   Window.bind(on_dropfile=self.on_drop_file)  # on_drop_file :: to be used as async function
  #
  # def _playItem_pressedOnce_(self, wid=None):
  #   if self._focus_ is None:
  #     wid.on_leave()
  #     color = wid.normal.copy()
  #     wid.normal = (.3, .1, 0, 1)
  #     wid._pressed_ = True
  #     wid.on_enter()
  #     self._focus_ = {'clr': color, 'wid': wid}
  #   else:
  #     if self._focus_['wid'] == wid:
  #       wid.on_leave()
  #       wid._pressed_ = None
  #       wid.normal = self._focus_['clr']
  #       wid.on_enter()
  #       self._focus_ = None
  #     elif type(self._focus_['wid']) is type([]) and wid in self._focus_['wid']:
  #       pass
  #     elif self._focus_.get('modifier'):
  #       if type(self._focus_['wid']) is type([]):
  #         pass
  #       else:
  #         pass
  #     else:
  #       self._focus_['wid']._pressed_ = None
  #       self._focus_['wid'].normal = self._focus_['clr']
  #       self._focus_ = None
  #       self._playItem_pressedOnce_(wid)
  #
  # def _playItem_pressedDouble_(self, wid=None):
  #   pass
  #
  # def show_loading_status(self, f=None):
  #   if not self.ids.dragger.children or self.ids.dragger.children[-1].name:
  #     self.__showLoader = 'on'
  #     loader = Loading()
  #     self.ids.dragger.add_widget(loader)
  #     loader.size_hint_x = None
  #     loader.width = loader.height
  #
  #   else:
  #     self.ids.dragger.remove_widget(self.ids.dragger.children[-1])
  #     self.__showLoader = None
  #
  # def _check_StartUp_autoPlay_(self, *largs):
  #   add_newDroppedTo_list(self)
  #   if self.__autoplay:
  #     Logger.warning("autoplay: Error-Check Failed!.")
  #     return
  #
  #   self.__autoplay = 'off'
  #   self.__index = 0
  #
  # def _ready_player_(self):
  #   _source_ = self._playList[self.__index]
  #
  #   if self.__player is None:
  #     self.__player = SoundLoader.load(_source_)
  #     self.__player.bind(
  #       source=self._source_changed_, state=self._state_changed_,
  #       volume=self._volume_changed_)
  #     self.length = AliasProperty(getter=self._getLength_,
  #                                 setter=self._setLength_, bind=["_duree_"])
  #     self.length = self.__player.length
  #   else:
  #     self.__player.source = _source_
  #
  #   self._playProtocol_()
  #
  # def _source_changed_(self, *largs):
  #   print("Source Changed to `%s`" % largs[1])
  #
  # def _state_changed_(self, *largs):
  #   print("State Changed to `%s`" % largs[1])
  #
  # def _volume_changed_(self, *largs):
  #   print("Volume Changed to `%s`" % largs[1])
  #
  # def _pos_changed_(self, *largs):
  #   print("Position Changing.. to `%s`" % largs[1])
  #
  # def _playProtocol_(self):
  #   self.__player.play()
  #   self.ids.track_Info.text = os.path.basename(self.__player.source)
  #
  # def _setLength_(self, value):
  #   self._duree_ = self.__player.length
  #
  # def _getLength_(self):
  #   return self._duree_
  #
  # def on_length(self, *largs):
  #   print("Length Changed to `%s`" % largs[1])
