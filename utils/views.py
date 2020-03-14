import re
import json
from utils.loggers import alert_, inform_
from os import listdir
from kivy.app import App
from threading import Thread
from utils.templates import *
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from utils.read_config import read_config
from kivy.uix.gridlayout import GridLayout
from utils.helpers import is_supported_format, duration_getter, \
    format_media_timestamp, digit_string_2_array


class GridLayer(GridLayout, CustomLayer):
    pass


class BoxLayer(BoxLayout, CustomLayer):
    pass


class HeadBarTemplate(BoxLayer, Dragging):
    title = StringProperty('')
    logo_name = StringProperty('')
    title_color = ListProperty([1, 1, 1, 1])
    disable_controls = OptionProperty('', options=['', '&ri', '&mi', 'mi&ri'])

    class HeadBarLogoInterface(Widget, IconFullPath):
        pace = NumericProperty(4)
        border_radius = ListProperty([0])
        cover_color = ListProperty([.3, .3, .35, 1])

    class HeadBarButtonInterface(ButtonTemplate):
        border_radius = [3]
        toggle_graffiti = NumericProperty(0)

        def on_hover(self):
            if not self.disabled:
                self.background_color = [1, 1, 1, .1]

        def on_leave(self):
            if not self.disabled:
                self.background_color = [0, 0, 0, 0]

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

        def on_disable_controls(self, interface, disabler):
            if disabler in ['&ri', 'mi&ri']:
                self.ids.resize.disabled = True
            elif disabler in ['&mi', 'mi&ri']:
                self.ids.minimize.disabled = True

        def _invoke_resizing(self, interface):
            pass

        def _invoke_closing(self, interface):
            pass

        def _invoke_minimizing(self, interface):
            pass

    class HeadBarDescription(Label):
        pass

    def __init__(self, **kwargs):
        super(HeadBarTemplate, self).__init__(**kwargs)
        self._apply_configs()

    def _apply_configs(self):
        pass


class AppHeadBar(HeadBarTemplate):
    draggable_obj = 'app'

    def _apply_configs(self):
        try:
            for option, value in read_config('head-bar'):
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


class DisplayPlayingTimestamps(Label, CustomLayer):
    """  """
    timestamp = NumericProperty(None, allownone=True)

    def on_timestamp(self, interface, value):
        self.text = format_media_timestamp(value) if value else '--:--'


class PlayingMediaInfoBar(BoxLayer):
    pass


class LeftMenuNavigator(BoxLayer):
    pass


class LeftMenuElement(GridLayout):
    pass


class TypicalPlaylist(BoxLayer, Clicking, Hovering):
    title = StringProperty('')

    def playback_finished(self, index):
        prop_index = len(self.children) - (1 + index)
        self.children[prop_index].change_playing_color()

    def get_another(self, index, _loop, _random):
        if not self.children:
            return
        # increment index only if _loop allows it
        if _loop != 'one':
            # incrementing current index value so to access associated media
            index += 1
        # in case the index is last in line and there is continuous loop enabled return
        if index == len(self.children):
            if _loop != 'all':
                return
            if _random and len(self.children) > 2:
                self.randomize_media(index)
            else:
                self.children[-1].on_down()
        # in case the index is less than 0, it means user performed previous action
        # when the currently playing media index is 0
        elif index < 0:
            self.children[len(self.children) - 1].on_down()
        # when randomize is enabled
        elif _random and len(self.children) > 2:
            self.randomize_media(index)
        # see the index we have is proportional the mechanism widgets use to order their children,
        # so here I'm going to normalize index to be proportional with widget ordering algorithm
        else:
            propo_index = len(self.children) - (1 + index)
            child = self.children[propo_index]
            if child.selected:
                child.on_down()
            child.on_down()

    def randomize_media(self, index):
        from random import randrange
        # shaking the index list to pick one by chance
        random_index = randrange(0, len(self.children))
        # normalize randomized index to be player proportional
        normal_index = len(self.children) - (1 + random_index)
        # in case both current supposedly index and randomized one equal, swap normal and randomized
        if random_index == index:
            self.children[normal_index].on_down()
        else:
            self.children[random_index].on_down()


class VolumeTuner(LevelBar):

    def __init__(self, **kwargs):
        super(VolumeTuner, self).__init__(**kwargs)
        self._pre_configuring()

    def _pre_configuring(self):
        volume_scale = read_config('player', 'volume')
        self.level = self.width * float(volume_scale)


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


class VideoAudioPlayer(Screen):
    # An engine for audio medias
    _audioModular = ObjectProperty(None, allownone=True)
    # An engine for video medias
    _videoModular = ObjectProperty(None, allownone=True)
    # A threaded cpu-clock for reading current position audio playing media
    _audioPositionThread = None
    # current loaded media source file
    _source = StringProperty('')
    # default volume of media player
    _volume = NumericProperty(0.5)
    # Position value to jump to while the media is in play or pause state
    _seek_pos = NumericProperty(None, allownone=True)
    # Estimated media lasting period
    _duration = NumericProperty(None, allownone=True)
    # Current elapsed time-frame of the media
    _current_pos = NumericProperty(None, allownone=True)
    # media player functioning status
    _state = OptionProperty('stop', options=['stop', 'play', 'pause'])
    # Repeating feature status of the media player
    _loop = OptionProperty('none', options=['none', 'one', 'all'])
    # randomizing status of the media player
    _shuffle = BooleanProperty(False)
    # identifier for intentional cease of media functionality
    _forcedStop = BooleanProperty(False)
    _nextIndex = NumericProperty(None, allownone=True)
    _currentIndex = NumericProperty(None, allownone=True)
    prevent_play_another = None
    _keypadInterface = None

    def on_enter(self, window):
        """ When mouse enters player, invoke acquire keypad and invoke keypad control directive protocol """
        try:
            self._keypadInterface = window.request_keyboard(self._keypadInterface_detached, self)
            self._keypadInterface.bind(on_key_down=self._command_media_directives_with_keypad_)
        except Exception as exc:
            # -- snippets -- to inform user that keypad directives are not available
            alert_(f'Failed to acquire keyboard due to {exc}')

    def on_leave(self, window=None):
        """ When mouse leaves player, release keypad interface, and disengage keypad control directive protocol """
        try:
            if self._keypadInterface:
                self._keypadInterface.unbind(on_key_down=self._command_media_directives_with_keypad_)
                self._keypadInterface = None
        except Exception as exc:
            alert_(
                f'''Failed to detach keypad-interface due to {exc}
                    ..Deploying keypadInterface-detach counter-measure
                '''
            )
            self.on_leave()

    def _command_media_directives_with_keypad_(self, interface, keyCode, character, modifier):
        """ keypad directives for commanding media player """

        if character == 's':
            self.stop_playback()
        elif character == 'n':
            self._next()
        elif character == 'p':
            self._previous()
        elif character == 'l':
            self._loop_alter(self.ids.loope)
        elif character == 'm':
            self._volume_tuning_keypad_directive('mute')
        elif character == 'r':
            self._shuffle_alter(self.ids.shufflee)
        elif character == 'e':
            self.headBar_hypothesis('mini')
        elif character == 'd':
            self.headBar_hypothesis('dock')
        elif character == 'f':
            self.headBar_hypothesis('full')
        elif character == 'q':
            self.headBar_hypothesis('quit')
        elif keyCode[1] == 'spacebar':
            self.play_pause(self.ids.pp)
        elif keyCode[1] == 'up' and 'ctrl' in modifier:
            self._volume_tuning_keypad_directive('up')
        elif keyCode[1] == 'down' and 'ctrl' in modifier:
            self._volume_tuning_keypad_directive('down')
        elif keyCode[1] == 'left' and 'shift' in modifier:
            self.backward_wind()
        elif keyCode[1] == 'right' and 'shift' in modifier:
            self.forward_wind()

    def _keypadInterface_detached(self):
        """ After the keypad has served its purpose, it gets released to reduce memory allocated """
        pass

    def _volume_tuning_keypad_directive(self, action):
        """ Volume regulation analysis based on keypad directive """

        volumeTuner = self.ids.volTuner
        if action == 'up':
            volumeScale = volumeTuner.level + (volumeTuner.size[0] * .05)
        elif action == 'down':
            volumeScale = volumeTuner.level - (volumeTuner.size[0] * .05)
        elif action == 'mute':
            self._mute()
            return

        if volumeScale < 0:
            volumeScale = 10e-24
        elif volumeScale > volumeTuner.width:
            volumeScale = volumeTuner.width
        volumeTuner.level = volumeScale

    @staticmethod
    def _size_modulation_keypad_directive(action):
        """ Resizing analysis of keypad directive """

        if action == 'F':
            pass
        elif action == 'E':
            pass
        elif action == 'D':
            pass
        elif action in ('Q', 'ESC'):
            pass

    def _is_media_loaded(self, state=None):
        """ To find out if player is ready to read loaded media source """
        return self._audioModular or self._videoModular

    def playing_request_from_(self, source, index):
        """ Communication stream from playlists to player """

        if self._source:
            self.prevent_play_another = True
            self.apply_stop()
        # assign current media source index from its container
        self._currentIndex = self._nextIndex = index
        # media source address to load its data
        self._source = source

    def on_source(self, interface, new_source):
        """ A trigger when player source path changes """

        if not new_source:
            return
        self._player_prepping_routine(new_source, is_supported_format(new_source))

    def _player_prepping_routine(self, media_source, modular):
        """ decides on which rightful modular to use given the format of media_source """
        pass

    def on_volume(self, interface, intensity):
        """ A trigger to apply volume compliance when changes occur """

        if self._audioModular:
            self._audioModular.volume = intensity
        elif self._videoModular:
            self._videoModular.volume = interface

    def on_state(self, interface, status):
        """ A trigger to invoke certain protocols when changes occur to player state """
        pass

    def on_seek_pos(self, interface, jump_to):
        """  triggers certain protocols when changes occur """

        if jump_to is None:
            return
        if self._videoModular:
            pass
        if self._audioModular:
            pass
        # After certain protocols have completed their routines, reset this value default
        self._seek_pos = None

    def on_duration(self, interface, lifetime):
        """ triggers protocols for updating-UI when changes occur """
        pass

    def on_current_pos(self, interface, pos_at):
        """ triggers protocols for UI-updating when changes occur """

        if pos_at is None:
            return

    def _manual_duration_getter_for_audios(self):
        """ cpu-clocked targeted for retrieving playing media duration lifetime value
            And more, initiates a threaded cpu-clock getter for current position
            This applies only on audio medias
        """

        media_duration = duration_getter(self.source)
        if (media_duration <= 0) or (type(media_duration) is not float):
            Clock.schedule_once(lambda *largs: self._manual_duration_getter_for_audios(), .28)
        else:
            self.duration = media_duration
            self._audioPositionThread = Thread(
                target=Clock.schedule_interval,
                args=(self._manual_pos_getter_for_audios, .48)).start()

    def _manual_pos_getter_for_audios(self, *largs):
        current_pos = self._audioModular.get_pos()
        self.current_pos = 0 if current_pos < 0 else current_pos

    def on_modular_state(self, modular, status):
        """ triggers certain routines when such Modular state changes """

        if status == 'play':
            pass
        elif status == 'pause':
            pass
        else:
            pass

    def _stopping_routine(self):
        """ collective actions to be carried out if player is to stop reading operations """
        pass

    def _pausing_routine(self):
        """ collective actions to be carried out if player is to freeze reading operations """
        pass

    def _playing_routine(self):
        """ certain changes and updates to be applied when player enters reading operations """
        pass

    def _resuming_routine(self):
        """ Bunch of actions to be carried out when resuming player operations """
        pass

    def _resuming_audio_sub_routine(self):
        """ Other necessary key changes to make when resuming audio media """
        pass

    def _player_resetting_routine(self):
        """ reset player to default means undo all changes made to it or in its behalf """
        pass

    def _nextInline_to_play_routine(self):
        """ decides on whether player should continues its operations or not """
        pass

    def _clear_modularTriggers(self):
        """ clears changes-observers to modular attributes """
        pass

    def _create_modularTriggers(self):
        """ adds changes-observers to modular attributes """
        pass

    def _create_playerProgress_levelTriggers(self):
        """ adds changes-triggers to progress bars of the players """
        pass

    def pauseAndPlay_(self, interface):
        """ motion event of pause and play interface-actors """
        pass

    def stop_(self, interface):
        """ motion events of stop interface-actor """
        pass

    def forward_(self, interface):
        """ motion events of forward interface-actor """
        pass

    def backward_(self, interface):
        """ motion events of backward interface-actor """
        pass

    def next_(self, interface):
        """ motion events of next interface-actor """
        pass

    def previous_(self, interface):
        """ motion events of previous interface-actor """
        pass

    def loop_(self, interface):
        """ motion events of loop interface-actor """
        pass

    def shuffle_(self, interface):
        """ motion events of shuffle interface-actor """
        pass


class Recorder(Screen):
    pass


class ImageViewer(Screen):
    pass


class BroadcastPlayer(Screen):
    pass


class Downloader(Screen):
    pass


class Splashing(BoxLayer):
    pass


class SyaiV3Play(BoxLayer):

    def __init__(self, **kwargs):
        super(SyaiV3Play, self).__init__(**kwargs)
        self._apply_configsOn_startup()

    def _apply_configsOn_startup(self):
        """ configuring main app view with pre-saved settings """

        back_color = read_config('main', 'back_color')
        self.background_color = digit_string_2_array(back_color, float)

    def process_cli_inputs(self, *largs):
        """ Capture all inputs from command line on startup """
        print(largs)

    def _ready_routine(self):
        """ called after startup dynamic resizing completes """
        pass

    def _activate_dragAndDrop_tunel(self):
        Window.bind(on_dropfile=self._processing_dropped_file)

    def _processing_dropped_file(self, *largs):
        if self.dropping is None:
            # mapping a dropping status widget
            self.show_dropping_status()
            # creating after dropping counter measure
            self.dropping = Clock.schedule_once(self.after_all_dropped, 1.4)
        # freezing after dropping counter measure just to sort a dropped file
        self.dropping.cancel()
        # decoding dropped file to <class str>
        dropped_file = largs[1].decode('utf-8')
        self.verify_file_address(dropped_file)
        # unfreeze after dropping counter measure
        self.dropping()
