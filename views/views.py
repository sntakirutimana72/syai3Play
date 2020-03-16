import re
import json
from utils.loggers import alert_, inform_
from os import listdir
from kivy.app import App
from threading import Thread
from guix import templates as uix
from guix.headbar import HeadBar
from guix.levelbar import LevelBar
from guix.customlayers import CustomLayer
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from utils.read_config import read_config
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ListProperty, BooleanProperty, \
    StringProperty, OptionProperty, NumericProperty, ObjectProperty
from utils.helpers import is_supported_format, duration_getter, \
    format_media_timestamp, digit_string_2_array
from kivy.lang import Builder


Builder.load_string("""
<SyaiV3Play>:
    orientation: 'vertical'

    AppHeadBar:  # 1-layout
    BoxLayout:  # 2-layout
        orientation: 'vertical'
        BoxLayer:  # 2.1-layout ~ aka menu-bar
            # background_color: [.28, .28, .26, 1]
            size_hint_y: None
            height: dp(24)
        BoxLayout:  # 2.2-layout
            BoxLayout:  # 2.2.1-layout
                size_hint_x: None
                width: min(dp(400), root.width * .33)
                BoxLayer:  # 2.2.1.1-layout ~ aka category search-engine
                    size_hint_y: None
                    height: dp(34)
                BoxLayer:  # 2.2.1.2-layout ~ aka category&sub contents
                BoxLayer:  # 2.2.1.3-layout ~ aka category&sub menu
                    size_hint_y: None
                    height: dp(34)
            BoxLayout:  # 2.2.2-layout
                ScreenManager:  # 2.2.2.1-layout ~ modulars manager
                BoxLayout:  # 2.2.2.2-layout ~ aka current modular working list
                    size_hint_x: None
                    orientation: 'vertical'
                    width: min(dp(220), self.parent.width * .35)
                    BoxLayer:  # 2.2.2.2.1-layout ~ aka c.w.l. search-engine
                        size_hint_y: None
                        height: dp(34)
                    ScrollView:  # 2.2.2.2.2-layout ~ aka c.w.l. scroller
                        GridLayer:  # 2.2.2.2.2.1-layout ~ aka c.w.l.
                            cols: 1
                            size_hint_y: None
                            height: max(self.minimum_height, self.parent.height)
    BoxLayer:  # 4-layout ~ aka modulars info-display and menu
        # background_color: [.12, .12, .15, 1]
        size_hint_y: None
        height: dp(28)

""")


class AppHeadBar(HeadBar):
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

    def on_close(self):
        # terminating all running app processes
        App.stop(App.get_running_app())

    def on_resize(self):
        pass

    def on_minimize(self):
        # minimizing agent
        App.get_running_app().root_window.minimize()


class DisplayPlayingTimestamps(Label, CustomLayer):
    """  """
    timestamp = NumericProperty(None, allownone=True)

    def on_timestamp(self, interface, value):
        self.text = format_media_timestamp(value) if value else '--:--'


class PlayingMediaInfoBar(uix.BoxLayer):
    pass


class LeftMenuNavigator(uix.BoxLayer):
    pass


class LeftMenuElement(GridLayout):
    pass


class VolumeTuner(LevelBar):

    def __init__(self, **kwargs):
        super(VolumeTuner, self).__init__(**kwargs)
        self._pre_configuring()

    def _pre_configuring(self):
        volume_scale = read_config('player', 'volume')
        self.level = self.width * float(volume_scale)


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


class Splashing(uix.BoxLayer):
    pass


class SyaiV3Play(uix.BoxLayer):

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