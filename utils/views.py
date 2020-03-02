from threading import Thread
from kivy.clock import Clock
from kivy.lang import Builder
from utils.templates import *
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from utils.helpers import is_supported_format, duration_getter, format_media_timestamp


Builder.load_string("""
<CustomLayer>:
    canvas.before:
        Color:
            rgba: self.background_color
        RoundedRectangle:
            radius: self.radius
            pos: self.pos
            size: self.size
        Color:
            rgba: self.outline_color
        Line:
            width: 1 if self.outline_width is None else self.outline_width
            rounded_rectangle: (*self.pos, *self.size, *self.radius)


<LevelBar>:
    canvas:
        Color:
            rgba: self.level_color
        RoundedRectangle:
            radius: self.radius
            pos: self.x + 1.5, self.y + 1.5
            size: self.level - 3, self.size[1] - 3

        Color:
            rgba: self.handle_color
        Ellipse:
            pos: (self.x + self.level - (self.height + 10) / 2, self.y - 5)
            size: (self.height + 10, self.height + 10)
            source: self.handle_image
""")


class DisplayPlayingTimestamps(Label, CustomLayer):
    """  """
    timestamp = NumericProperty(None, allownone=True)

    def on_timestamp(self, interface, value):
        self.text = format_media_timestamp(value) if value else '--:--'


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
    font_name = 'RobotoMono-Regular'
    color = [0, 1, 1, 1]
    font_size = 9
    markup = True

    def on_textVal(self, *largs):
        if not largs[1]:
            return
        if self.display_type == 'vol':
            val = 'vol ' + largs[1] + ' [color=#f00]%[/color]'
        elif self.display_type == 'format':
            val = 'format: ' + largs[1]
        elif self.display_type == 'state':
            val = 'status: ' + largs[1]

        self.text = val
        self.textVal = ''


class GridLayer(GridLayout, CustomLayer):
    pass


class BoxLayer(BoxLayout, CustomLayer):
    pass


class LeftNavMenu(BoxLayer):
    focused = None

    strip_size = NumericProperty(6)
    '''width size value for the splitter
      :attr: is a :class:`~kivy.properties.NumericProperty` and default to 6
    '''
    strip_backgroundImg = StringProperty('')
    '''splitter background image if preferred
      :attr: is a :class:`~kivy.properties.StringProperty` and default to ''
    '''
    strip_backgroundClr = ListProperty([.3, .3, .4, .3])
    '''splitter background color
      :attr: is a :class:`~kivy.properties.ListProperty` and default to [.8, .8, 1, .05]
    '''
    strip_hoverClr = ListProperty([.6, .6, 1, .1])
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
        # self.normal = json.loads(SETTINGS.get('leftNav', 'background_color'))
        self.width = self.min_size
        if self.min_size > self.max_size:
            self.min_size = self.max_size

    def alter_focus(self, focus):
        if self.focused:
            if self.focused is focus:
                self.focused = None
                return
            self.focused.alter_selection()
        self.focused = focus

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


class NavElement(GridLayout):
    grand_parent = ObjectProperty(None)
    contents = ObjectProperty(None)
    is_open = BooleanProperty(False)
    selected = BooleanProperty(None)

    source = StringProperty('')
    font_size = NumericProperty('11sp')
    normal = ListProperty([0, 0, 0, 0])
    color = ListProperty([.6, 1, .6, 1])
    title = StringProperty('Element title')
    selected_normal = ListProperty([.6, .7, 1, .05])
    font_name = StringProperty('RobotoMono-Regular')

    def __init__(self, **kwargs):
        self.register_event_type('on_collapse_expand')
        super(NavElement, self).__init__(**kwargs)

    def on_parent(self, *largs):
        if largs[1]:
            self.decide_on_contents()

    def on_touch_down(self, touch):
        if self.ids.head_title.collide_point(*touch.pos):
            self.dispatch('on_collapse_expand')
            return True
        return super(NavElement, self).on_touch_down(touch)

    def on_collapse_expand(self):
        if self.contents:
            self.alter_selection()
            if self.grand_parent:
                self.grand_parent.alter_focus(self)

    def alter_selection(self):
        self.selected = not self.selected

    def decide_on_contents(self, *largs):
        if self.is_open:
            if not (self.ids and self.contents):
                Clock.schedule_once(self.decide_on_contents, .2)
            else:
                self.unbind(selected=self.on_selected)
                self.selected = True
                self.on_selected('', 1)
                self.bind(selected=self.on_selected)
        else:
            if not (self.ids and self.contents):
                Clock.schedule_once(self.decide_on_contents, .2)
            else:
                self.selected = False

    def on_selected(self, *largs):
        if not self.contents:
            return

        if largs[1]:
            if largs[1] is True:
                self.add_widget(self.contents)
            self.normal = [1, 1, .6, .05]
        else:
            self.remove_widget(self.contents)
            self.normal = [0, 0, 0, 0]
        self.is_open = not self.is_open

    def compute_height(self):
        return 25 if not self.contents else (26 + self.contents.size[1])


class SinglePlaylist(NavElement):
    source = 'Icons/playlist2.png'

    def on_selected(self, *largs):
        super(SinglePlaylist, self).on_selected(*largs)
        if largs[1] and self.grand_parent.is_viable_to_change_activePlaylist():
            self.grand_parent.activePlaylist = self.title


# class PlaylistManager(NavElement):
#     focused = None
#     source = 'Icons/playlist.png'
#
#     playlistOldTitle = None
#     enablePlaylistDelete = BooleanProperty(True)
#     '''Used to enable and disable a button of deleting a playlist
#         if True the deleting button is disabled otherwise is enabled
#     :attr:`enablePlaylistDelete` is a :class:`~kivy.properties.BooleanProperty` and
#                                                   default to True
#     '''
#     enablePlaylistRename = BooleanProperty(True)
#     '''Used to enable and disable a button of renaming a playlist
#         if True the renaming button is disabled otherwise is enabled
#     :attr:`enablePlaylistRename` is a :class:`~kivy.properties.BooleanProperty` and
#                                                   default to True
#     '''
#     activePlaylist = StringProperty('')
#     '''A reference object-id-name to the being used playlist. Mostly the playlist being played
#         is the active one but if there is none being played, the active one is activated
#             by a double click
#     :attr:`activePlaylist` is a :class:`~kivy.properties.StringProperty` and default to ''
#     '''
#     savingQueue = None
#     '''Used to hold all new playlists to be saved
#     :attr:`pendingQueue` is a :class:`~python.dict` and default to None
#     '''
#     savingState = None
#     '''used to indicate that the saving process has been initiated
#     :attr:`unloadingState` is a :class:`~python.bool` and default to None
#     '''
#     pendingQueue = None
#     '''Used to hold an new coming in lists temporarily in case there is one already in progress
#     :attr:`pendingQueue` is a :class:`~python.dict` and default to None
#     '''
#     unloadingState = None
#     '''used to prevent more than one queue to enter unloading process at the same time
#     :attr:`unloadingState` is a :class:`~python.bool` and default to None
#     '''
#     unloadingQueue = None
#     ''' Used to hold an active load queue data
#     :attr:`unloadingQueue` is a :class:`~python.list` and default to None
#     '''
#
#     def alter_focus(self, focus):
#         if self.focused:
#             if self.focused is focus:
#                 self.focused = None
#                 self.contents.size[1] -= 228
#                 self.enable_functionality(False)
#                 return
#             self.focused.alter_selection()
#         else:
#             self.contents.size[1] += 228
#         self.focused = focus
#         self.enable_functionality(True)
#
#     @staticmethod
#     def is_viable_to_change_activePlaylist():
#         root = App.get_running_app().root
#         return root.ids.play3GUIs.is_ready(True)
#
#     def on_activePlaylist(self, *largs):
#         root = App.get_running_app().root
#         root.ids.head_bar.currentPlaylist = largs[1]
#
#     def _decisionOn_newList(self, new_list):
#         # checking if the activePlaylist is a NoneType
#         active_name = 'unnamed playlist' if not self.activePlaylist else self.activePlaylist
#         # trigger playlist save in a local file to be reused later on when needed
#         self.trigger_playlist_save_mode(new_list, active_name)
#         # checking if there's no active un-listing progress
#         if self.unloadingState:
#             # checking if pendingQueue is a NoneType
#             if self.pendingQueue is None:
#                 self.pendingQueue = []
#             # storing the new_list to a waiting list
#             new_queue = {active_name: new_list}
#             self.pendingQueue.append(new_queue)
#         else:
#             # activating unloading progress
#             self.unloadingState = True
#             # charge or load queue
#             self.unloadingQueue = new_list
#             # directive for adding new_list items to a widget
#             self.init_unloading_directive(active_name)
#
#     def init_unloading_directive(self, _name):
#         # if new_list is > 160 length, thread the progress else normal progress
#         # threading a new progress prevents it from freezing other application activities
#         iteration_rate = len(self.unloadingQueue)
#         if iteration_rate > 160:
#             unListing_thread = Thread(
#                 target=self.unloadingProgress, name=_name, args=(_name,))
#             unListing_thread.start()
#         else:
#             self.unloadingProgress(_name)
#
#     def unloadingProgress(self, _name, is_threaded=None):
#         iteration_rate = len(self.unloadingQueue)
#         if is_threaded is None:
#             is_threaded = False if iteration_rate <= 160 else True
#
#         for _ in range(iteration_rate):
#             Clock.schedule_once(
#                 lambda x: self.add_media_to_playlist(_name), 0) \
#                 if is_threaded else self.add_media_to_playlist(_name)
#
#         Clock.schedule_once(lambda x: self.after_unloading_directive(_name), 1.25)
#
#     def after_unloading_directive(self, list_name):
#         if self.unloadingQueue:
#             Clock.schedule_once(lambda x: self.after_unloading_directive(list_name), .25)
#             return
#
#         # invoke autoplay-protocol to check if the first time auto play is feasible
#         self.init_autoplay_protocol(list_name)
#         # checking if there still some pending loads to work on
#         # if some found, process them in a threaded task
#         if self.pendingQueue:
#             # getting the next up queue in a line
#             nextQueue = self.pendingQueue.pop(0)
#             # freeing memory occupied by :attr:`pendingQueue` if no longer viable
#             if not self.pendingQueue:
#                 self.pendingQueue = None
#             # accessing nextQueue name to be used as playlist name to assign to
#             queue_name = list(nextQueue.keys())[0]
#             # charge or load an active queue
#             self.unloadingQueue = nextQueue
#             # threading unloading process
#             threadedUnload = Thread(
#                 target=self.unloadingProgress, args=(queue_name, True), name=queue_name)
#             threadedUnload.start()
#         else:
#             # perform last task to complete unloading process
#             self.unloadingProcess_complete()
#
#     def add_media_to_playlist(self, p_name):
#         if not self.unloadingQueue:
#             return
#         filet = self.unloadingQueue.pop(0)
#         playlist = self.does_playlist_exists(p_name)
#         media_node = PlayItem(fileSource=filet)
#         playlist.ids.play_list.add_widget(media_node)
#
#     def unloadingProcess_complete(self, *largs):
#         # clearing memory occupied with pending and unloading queues
#         # and resetting them back to initial state
#         self.unloadingQueue = self.pendingQueue = None
#         # clearing memory occupied by unloadingState and resetting it to initial
#         self.unloadingState = None
#         # informing the root widget that the process of handling the sent list is done
#         # so that the root may cease the activity of progress status
#         root = App.get_running_app().root
#         root.remove_dropping_status()
#
#     def enable_functionality(self, val):
#         self.enablePlaylistDelete = self.enablePlaylistRename = val
#
#     def _create_playlist(self):
#         name_input = PlaylistNameInput()
#         name_input.children[0].bind(focus=self.check_playlist_name)
#         pos_index = len(self.contents.children) - 1
#         self.contents.add_widget(name_input, pos_index)
#
#     def _rename_playlist(self):
#         # title = self.focused.ids.head_title
#         # self.playlistOldTitle = {'parent': title.parent, 'title': title}
#         # title.parent.remove_widget(title)
#         # _rename = PlaylistNameInput(text=self.focused.title, on_parent=self._attachOldTitle)
#         # _rename.children[0].focus = True
#         # _rename.children[0].bind(focus=self.check_playlist_new_name)
#         # self.focused.add_widget(_rename, 1)
#         pass
#
#     def _attachOldTitle(self, *largs):
#         # if self.playlistOldTitle and not largs[1]:
#         #   parent = self.playlistOldTitle['parent']
#         #   title = self.playlistOldTitle['title']
#         #   self.playlistOldTitle = None
#         #   parent.add_widget(title, 1)
#         # super(PlaylistNameInput, largs[0]).on_parent(*largs)
#         pass
#
#     def check_playlist_new_name(self, *largs):
#         if largs[0].parent.parent and not largs[1]:
#             playlist_name = largs[0].text
#             if not self.verify_playlist_name(playlist_name):
#                 largs[0].parent.text = largs[0].text = playlist_name
#                 self.remove_widget(largs[0].parent)
#             else:
#                 largs[0].text = largs[0].parent.text
#
#     def _delete_playlist(self):
#         pass
#
#     def check_playlist_name(self, *largs):
#         if largs[0].parent.parent and not largs[1]:
#             playlist_name = largs[0].text
#             if not self.verify_playlist_name(playlist_name):
#                 self.contents.remove_widget(largs[0].parent)
#                 self.init_singlePlaylist(playlist_name)
#             else:
#                 largs[0].text = largs[0].parent.text
#
#     def verify_playlist_name(self, p_name):
#         pRegex = re.compile(r'^[a-zA-Z0-9]{2,}(\s[a-zA-Z0-9]+)*$')
#         if p_name.lower() == 'enter playlist name' or not pRegex.search(p_name):
#             return True
#         return bool(self.ids.get(p_name))
#
#     def does_playlist_exists(self, i_name):
#         playlist_exist = self.ids.get(i_name)
#         if not playlist_exist:
#             playlist_exist = self.init_singlePlaylist(i_name)
#         return playlist_exist
#
#     def init_singlePlaylist(self, i_name):
#         new_playlist = SinglePlaylist(title=i_name, grand_parent=self)
#         self.contents.add_widget(new_playlist)
#         self.contents.size[1] += 28
#         self.ids[i_name] = new_playlist
#         return new_playlist
#
#     def init_autoplay_protocol(self, _name):
#         root = App.get_running_app().root
#
#         # checking if auto play is feasible
#         if not root.ids.play3GUIs.is_ready():
#             # getting active playlist name
#             if not self.activePlaylist:
#                 self.activePlaylist = _name
#
#             # accessing a playlist associated to the name pulled
#             uniquePlaylist = self.ids[self.activePlaylist]
#             # accessing songs list direct parent/container
#             songManager = uniquePlaylist.ids.play_list
#             # accessing the first song item in line
#             firstSongInLine = songManager.children[-1]
#             # generating a touch event on the first song item in line
#             firstSongInLine.on_down()
#
#     # div - handles playlist and other functions possible
#     # when saving, fetching, and updating playlist local file
#     def trigger_playlist_save_mode(self, queue, q_name):
#         if self.savingQueue is None:
#             self.savingQueue = []
#         self.savingQueue.append({q_name: (queue,)})
#
#         if self.savingState is None:
#             self.savingState = True
#             savingProcess = Thread(
#                 target=self.save_playlist_data, name='playlists save mode', daemon=True)
#             savingProcess.start()
#
#     def save_playlist_data(self):
#         while 1:
#             if not self.savingQueue:
#                 self.finalize_savingProcess()
#                 return
#
#             upQueue = self.savingQueue.pop(0)
#             queue_name = list(upQueue.keys())[0]
#             queue_data = upQueue.get(queue_name)
#             upQueue = None
#             if len(queue_data) > 1:
#                 self.apply_playlist_updates(queue_name, queue_data)
#             else:
#                 self.apply_playlist_save(queue_name, queue_data)
#
#     def apply_playlist_updates(self, q_name, q_data):
#         pass
#
#     def apply_playlist_save(self, q_name, q_data):
#         try:
#             json_data = self.open_playlistJSON()
#             if json_data:
#                 playlists = json_data.get('playlists')
#                 namedPlaylist = playlists.get(q_name)
#                 if namedPlaylist:
#                     namedPlaylist.extend(q_data[0])
#                 else:
#                     playlists.setdefault(q_name, q_data[0])
#         except:
#             pass
#         finally:
#             playlists = namedPlaylist = None
#             self.save_JSONData(json_data)
#
#     def finalize_savingProcess(self):
#         pass
#
#     def open_playlistJSON(self, mode='r'):
#         try:
#             with open("./syai3Play/data.json", mode) as json_object:
#                 json_data = json.load(json_object)
#         except Exception as exc:
#             Logger.error('SYAI3Play: Cannot data file due to <{}>'.format(exc))
#         finally:
#             return json_data
#
#     def save_JSONData(self, JSONdata):
#         try:
#             with open("./syai3Play/data.json", 'w') as json_object:
#                 json.dump(JSONdata, json_object)
#         except Exception as exc:
#             Logger.error('SYAI3Play: Cannot save file due to <{}>'.format(exc))
#
#
# class PlayItemManager(GridLayout):
#     focused = ObjectProperty(None, allownone=True)
#     ''' contains the selected child
#     :attr:`focused` is a :class:`~kivy.properties.ObjectProperty` and
#         default to None
#     '''
#
#     def on_new_focused(self, child):
#         if self.focused is child:
#             self.focused = None
#         else:
#             if self.focused:
#                 self.focused.admit_focus()
#             self.focused = child
#             child.change_playing_color()
#
#     def on_focused(self, *largs):
#         if not largs[1]:
#             return
#         root = App.get_running_app().root
#         focused_index = self.children.index(largs[1])
#         index = len(self.children) - (1 + focused_index)
#         root.ids.play3GUIs.autoPlay_backDoor(largs[1].fileSource, index)
#
#     def playback_finished(self, index):
#         prop_index = len(self.children) - (1 + index)
#         self.children[prop_index].change_playing_color()
#
#     def get_another(self, index, _loop, _random):
#         if not self.children:
#             return
#         # increment index only if _loop allows it
#         if _loop != 'one':
#             # incrementing current index value so to access associated media
#             index += 1
#         # in case the index is last in line and there is continuous loop enabled return
#         if index == len(self.children):
#             if _loop != 'all':
#                 return
#             if _random and len(self.children) > 2:
#                 self.randomize_media(index)
#             else:
#                 self.children[-1].on_down()
#         # in case the index is less than 0, it means user performed previous action
#         # when the currently playing media index is 0
#         elif index < 0:
#             self.children[len(self.children) - 1].on_down()
#         # when randomize is enabled
#         elif _random and len(self.children) > 2:
#             self.randomize_media(index)
#         # see the index we have is proportional the mechanism widgets use to order their children,
#         # so here I'm going to normalize index to be proportional with widget ordering algorithm
#         else:
#             propo_index = len(self.children) - (1 + index)
#             child = self.children[propo_index]
#             if child.selected:
#                 child.on_down()
#             child.on_down()
#
#     def randomize_media(self, index):
#         from random import randrange
#         # shaking the index list to pick one by chance
#         random_index = randrange(0, len(self.children))
#         # normalize randomized index to be player proportional
#         normal_index = len(self.children) - (1 + random_index)
#         # in case both current supposedly index and randomized one equal, swap normal and randomized
#         if random_index == index:
#             self.children[normal_index].on_down()
#         else:
#             self.children[random_index].on_down()
#
#
# class PlaylistNameInput(BoxLayer):
#     text = StringProperty('Enter Playlist Name')
#
#     def __init__(self, **kwargs):
#         super(PlaylistNameInput, self).__init__(**kwargs)
#         self.normal = [.2, .2, .2, 1]
#         self.radius = [4]
#         self.padding = [10, 0]
#         self.size_hint_y = None
#         self.height = 28
#         name_input = InputField(text=self.text)
#         self.add_widget(name_input)
#
#     def on_touch_down(self, touch):
#         if not self.collide_point(*touch.pos):
#             if self.parent:
#                 self.parent.remove_widget(self)
#         return super(PlaylistNameInput, self).on_touch_down(touch)
#
#     def on_parent(self, *largs):
#         root = App.get_running_app().root
#
#         if largs[1]:
#             root.ids.play3GUIs.on_leave(Window)
#             root.remove_window_cursor_listeners()
#         else:
#             root.add_window_cursor_listeners()
#             root.ids.play3GUIs.on_enter(Window)


class StreamsManager(NavElement):
    focused = None
    source = 'Icons/streams.png'

    def alter_focus(self, focus):
        if self.focused:
            if self.focused is focus:
                self.focused = None
                return
            self.focused.alter_selection()
        self.focused = focus


class DownloadManager(NavElement):
    focused = None
    source = 'Icons/downloads.png'

    def alter_focus(self, focus):
        if self.focused:
            if self.focused is focus:
                self.focused = None
                return
            self.focused.alter_selection()
        self.focused = focus


class FavoriteManager(NavElement):
    focused = None
    source = 'Icons/favorites.png'

    def alter_focus(self, focus):
        if self.focused:
            if self.focused is focus:
                self.focused = None
                return
            self.focused.alter_selection()
        self.focused = focus


class LoadingStatus(BoxLayout):
    message = StringProperty('Loading')
    '''Message to clarify what the loading status is about
    :attr:`message` is a :class:`~kivy.properties.StringProperty` and default to 'Loading'
    '''


class InputField(TextInput):
    write_tab = BooleanProperty(False)
    font_size = NumericProperty('11sp')
    multiline = BooleanProperty(False)
    cursor_color = ListProperty([1, 1, .7, 1])
    background_color = ListProperty([0, 0, 0, 0])
    foreground_color = ListProperty([.8, .5, .5, 1])
    font_name = StringProperty("RobotoMono-Regular")


# class HeadBar(GridLayer):
#     currentPlaylist = StringProperty('current playlist name')
#     ''' the name of the active or current working on playlist
#     '''
#     viewMode = OptionProperty('mini', options=['mini', 'dock', 'full'])
#     '''Used to set a proper view mode with relation its correspondent size
#
#       :attr: is a :class:`kivy.properties` and default to `mini`
#       ..Warning:: Only accepts of the its options values
#     '''
#     strippedViews = None
#     '''Temporal container for the stripped views to be reused when needed
#
#       :attr: is a :class:`<dict>` and default to None
#     '''
#
#     def __init__(self, **kwargs):
#         self.register_event_type('on_drag_window')
#         super(HeadBar, self).__init__(**kwargs)
#
#     def getProperty(self, prop_name):
#         return getProperty(prop_name)
#
#     def on_touch_down(self, touch):
#         if not (not (self.children[0].collide_point(
#                 *touch.pos) or self.children[1].children[0].collide_point(
#             *touch.pos)) and self.collide_point(*touch.pos)):
#             return super(HeadBar, self).on_touch_down(touch)
#
#         touch.grab(self)
#         Window.grab_mouse()
#         pos = pyauto.position()
#         left, top = Window.left, Window.top
#         self.drag_pos = [pos[0] - left, pos[1] - top]
#         return True
#
#     def on_touch_move(self, touch):
#         if touch.grab_current == self:
#             self.dispatch('on_drag_window')
#
#     def on_touch_up(self, touch):
#         if touch.grab_current == self:
#             touch.ungrab(self)
#             Window.ungrab_mouse()
#
#     def on_drag_window(self):
#         pos = pyauto.position()
#         Window.left, Window.top = (
#             pos[0] - self.drag_pos[0], pos[1] - self.drag_pos[1])
#
#     def do_minimize(self):
#         Window.minimize()
#
#     def do_resize(self):
#         root = App.get_running_app().root
#
#         if self.viewMode == 'full':
#             # preventing window from making auto view switching on resize
#             root.resizeLock = True
#
#             x, total_x = root.width, pyauto.size()
#             ratio = x / total_x[0]
#             if ratio >= .95:
#                 size = (650, total_x[1] * .5)
#             else:
#                 size = total_x
#             Window.size = size
#
#             # updating LeftNavMenu if when resizeLock is enabled
#             root.update_left_nav_size(size[0])
#             # re-enabling window to make auto view switching on resize
#             root.resizeLock = None
#         else:
#             self.switch_to_full_view()
#
#     def do_terminate(self):
#         #  An event for terminating the whole application processes pool
#         App.stop(App.get_running_app())
#
#     ''' A division of handling application possible views and Window resize
#           auto actions and switching mechanisms
#     '''
#
#     def _revealMoreOptions(self):
#         root = App.get_running_app().root
#         current_s = root.ids.disp_manager.current_screen
#         current_s.add_widget(MoreOptions(root=self))
#
#     def on_miniDockSwitch(self, mode):
#         if self.viewMode == mode:
#             return
#
#         root = App.get_running_app().root
#         root.resizeLock = True
#
#         if mode == 'mini':
#             self.switch_to_minimal_view()
#         else:
#             self.switch_to_dock_view()
#
#     def prep_stripped_container(self):
#         if self.strippedViews is None:
#             self.strippedViews = {}
#
#     def switch_to_minimal_view(self):
#         root = App.get_running_app().root
#
#         if self.viewMode == 'full':
#             # stripping left-nav from its parent
#             left_nav = root.ids.msc_cont.children[1]
#             left_nav.parent.remove_widget(left_nav)
#             # storing left-nav for later re-use
#             self.strippedViews['left-nav'] = left_nav
#             # Resizing Window after stripping
#             self.resize_window(450, 128)
#         else:
#             # accessing player GUIs container
#             play_gui = root.ids.play3GUIs
#             # retrieving row_2 view from store
#             row_2 = self.strippedViews['row_2']['self']
#             # stripping progress container from its current parent and re-assign it
#             progress_cont = play_gui.ids.row_1.children[0]
#             progress_cont.parent.remove_widget(progress_cont)
#             row_2.children[1].add_widget(progress_cont, 1)
#             # restoring row_2 to its original position and parent
#             row2_parent = self.strippedViews['row_2']['parent']
#             row2_parent.add_widget(row_2)
#             # deleting row_2 contents from store
#             del self.strippedViews['row_2']
#             # Resizing Window after stripping
#             Window.size = (450, 128)
#             # resetting root resizeLock value to automatic
#             root.resizeLock = None
#         # resetting view mode to minimal view mode
#         self.viewMode = 'mini'
#
#     def switch_to_dock_view(self):
#         root = App.get_running_app().root
#
#         if self.viewMode == 'full':
#             # stripping left-nav from its parent
#             left_nav = root.ids.msc_cont.children[1]
#             left_nav.parent.remove_widget(left_nav)
#             # storing left-nav for later re-use
#             self.strippedViews['left-nav'] = left_nav
#
#         # ensure strippedViews store won't be NoneType
#         self.prep_stripped_container()
#         # accessing player GUIs container
#         play_gui = root.ids.play3GUIs
#         # stripping row_2 view from its parent
#         row_2 = play_gui.ids.row_2
#         row2_parent = row_2.parent
#         row2_parent.remove_widget(row_2)
#         # stripping progress container view from its parent
#         progress_cont = row_2.children[1].children[1]
#         progress_cont.parent.remove_widget(progress_cont)
#         # storing stripped row_2 view
#         self.strippedViews['row_2'] = {'self': row_2, 'parent': row2_parent}
#         # volume container shrinking and misplacing
#         play_gui.ids.vol_cont.maximum_width = 90
#         # adding progress container to row_1
#         play_gui.ids.row_1.add_widget(progress_cont)
#
#         # Resizing Window after stripping
#         if self.viewMode == 'full':
#             self.resize_window(450, 68)
#         else:
#             Window.size = (450, 68)
#             # resetting root resizeLock to automatic react on resize
#             root.resizeLock = None
#
#         # resetting view mode to dock mode
#         self.viewMode = 'dock'
#
#     def switch_to_full_view(self):
#         root = App.get_running_app().root
#         root.resizeLock = True
#
#         if self.viewMode == 'dock':
#             # switching to minimal view mode first if required
#             self.switch_to_minimal_view()
#             # after calling the above method this lock is reset to auto so change to manual is needed
#             root.resizeLock = True
#
#         # ensure strippedViews store won't be NoneType
#         self.prep_stripped_container()
#         # retrieving left-nav if store earlier
#         left_nav = self.strippedViews.get('left-nav')
#         # checking if the left-nav was once already created
#         if not left_nav:
#             # creating the left-nav for the first time if necessary
#             left_nav = LeftNavMenu()
#         else:
#             # deleting the left-nav if found in store
#             del self.strippedViews['left-nav']
#         # assigning left-nav to a parent
#         root.ids.msc_cont.add_widget(left_nav, 1)
#         # resizing window to the minimal size of full mode view
#         self.resize_window(650, 250, .14)
#         # setting view mode indicator to full mode
#         self.viewMode = 'full'
#
#     def resize_window(self, x, y, d=.2):
#         animation = Animation(size=(x, y), d=d)
#         animation.bind(on_complete=self.resize_animation_complete)
#         animation.start(Window)
#
#     def resize_animation_complete(self, *largs):
#         root = App.get_running_app().root
#
#         if Window.size[0] == 650:
#             root.ids.msc_cont.children[1].width = root.size[0] - 450
#         # re-enabling auto mode view switching on window resize
#         root.resizeLock = None
#
#     def ensure_existenceOf_leftNav(self):
#         '''
#         It's to be used when adding dropped files to the playlist widget
#             located on the LeftNavMenu widget
#         :return:`left-nav` is a :class:`~kivy.property.ObjectProperty` and contains LeftNavMenu
#         '''
#         root = App.get_running_app().root
#
#         if self.viewMode != 'full':
#             # ensure strippedViews is not NoneType
#             self.prep_stripped_container()
#             left_nav = self.strippedViews.get('left-nav')
#             if not left_nav:
#                 # creating the left-nav for the first time if necessary
#                 left_nav = LeftNavMenu()
#                 # storing it
#                 self.strippedViews['left-nav'] = left_nav
#         else:
#             # accessing left-nav from root children
#             left_nav = root.ids.msc_cont.children[1]
#
#         return left_nav.ids.playlists


# class HrzProgressBar(HoverableLabel):
#     radius = ListProperty([0])
#     normal = ListProperty([.2, .2, .2, .3])
#     level_normal = ListProperty([.8, .1, 0, .2])
#     handler_normal = ListProperty([.2, .2, .2, 1])
#     handler_image = StringProperty('Icons/yellow.png')
#
#     progressLevel = NumericProperty(0.)
#     '''Track bar level in percentage 0.0%
#       :attr: is a :class:`~kivy.properties.NumericProperty` and default
#         to 0.0
#       ..Warnings:: it takes only decimal or real number not percentile
#     '''
#     stoppedAtLevel = NumericProperty(0.)
#     '''Track bar final level in percentage 0.0% after all motion events
#       :attr: is a :class:`~kivy.properties.NumericProperty` and default
#         to 0.0
#       ..Warnings:: it takes only decimal or real number not percentile
#     '''
#     visible = OptionProperty('none', options=['none', 'off', 'in', 'out'])
#     '''Adjuster or handler clocking capability
#       :attr: is a :class:`~kivy.properties.OptionProperty` and default
#         to None
#
#       ..Warning:: it takes only one among ['off', 'in', 'out', 'none']
#
#       :value::`off`: means the handler is invisible
#       :value::`in or out`: means the handler can switch between visible and invisible modes
#
#     '''
#     bar_active = BooleanProperty(True)
#     '''Disables & Enables the interactivity of the handler
#
#       :attr: is a :class:`~kivy.properties.Boolean` and default to True
#       :False::`disables`
#       :True::`Enables`
#     '''
#     autoSwitchMode = None
#     '''Automates the visibility mode switching when :attr::visible::`is enabled`
#       :attr: is a :object:`~python const` and default to None
#     '''
#     widthConst = None
#     '''previous width container and to be used when auto resize triggered
#         in order to re-normalize progressLevel
#       :attr: is a :object:`~python const` and default to None
#     '''
#
#     def on_size(self, *largs):
#         if not self.progressLevel:
#             self.widthConst = largs[1][0]
#             return
#         self.re_normalize_level()
#
#     def on_bar_active(self, *largs):
#         if largs[1]:
#             self.reveal_handle()
#             self.visible = 'in'
#         else:
#             self.visible = 'off'
#
#         self.disabled = largs[1]
#
#     def on_enter(self):
#         if self.visible in ('off', 'none'):
#             return
#         self.autoSwitchMode.cancel()
#         self._changeVisibility()
#
#     def _changeVisibility(self, *largs):
#         self.visible = "out" if largs else "in"
#
#     def on_leave(self):
#         if self.visible in ('off', 'none'):
#             return
#         self.autoSwitchMode()
#
#     def on_visible(self, *largs):
#         if largs[1] == "out":
#             self.hide_handle()
#         elif largs[1] == "in":
#             if self.autoSwitchMode is None:
#                 self.autoSwitchMode = Clock.schedule_once(self._changeVisibility, 5)
#             else:
#                 self.reveal_handle()
#         elif largs[1] == 'off':
#             if self.autoSwitchMode:
#                 self.autoSwitchMode.cancel()
#                 self.autoSwitchMode = None
#             self.hide_handle()
#
#     def hide_handle(self):
#         self.handler_normal[-1] = 0
#
#     def reveal_handle(self):
#         self.handler_normal[-1] = 1
#
#     def on_touch_down(self, touch):
#         if self.collide_point(*touch.pos):
#             if self.bar_active:
#                 touch.grab(self)
#                 self._normalize_move_(touch.pos[0])
#             return True
#         return super(HrzProgressBar, self).on_touch_down(touch)
#
#     def on_touch_move(self, touch):
#         if touch.grab_current == self:
#             self._normalize_move_(touch.pos[0])
#         return True
#
#     def on_touch_up(self, touch):
#         if touch.grab_current == self:
#             self._finalPointLevel(touch.pos[0])
#             touch.ungrab(self)
#         return True
#
#     def _normalize_move_(self, pos_x):
#         self.progressLevel = self.compute_pos_val(pos_x)
#
#     def _finalPointLevel(self, pos_x):
#         self.stoppedAtLevel = self.compute_pos_val(pos_x)
#
#     def compute_pos_val(self, pos_x):
#         x = pos_x - self.x
#         if x < 0:
#             x = 0
#         elif x > self.size[0]:
#             x = self.size[0]
#         return x
#
#     def re_normalize_level(self):
#         self.progressLevel *= self.size[0] / self.widthConst
#         self.widthConst = self.size[0]
#
#
# class VolumeBar(HrzProgressBar):
#
#     def on_parent(self, *largs):
#         if largs[1]:
#             Clock.schedule_once(self.initial_player_volume, 1)
#
#     def initial_player_volume(self, *largs):
#         if self.size[0] < 101:
#             Clock.schedule_once(self.initial_player_volume, .02)
#         else:
#             vol = SETTINGS.getfloat('MEDIA', 'volume')
#             self.progressLevel = self.size[0] * vol
#
#
# class AutoRollLabel(ScrollInactiveBar):
#     text = StringProperty('')
#     color = ListProperty([.2, .2, .2, 1])
#     font_size = StringProperty('11sp')
#
#     autoScroll = BooleanProperty(False)
#     '''Indicates whether the property of scrolling is automated or hovered
#        :attr: is a :class:`kivy.properties.Boolean` and default to False
#        ..Info::`if False it only scrolls on hover else scheduled for every some seconds
#     '''
#     scrollHandler = None
#     '''Object reserved for auto-scrolling re-schedule when is active as to re-initiate auto-scrolling
#        every some seconds after the previous scrolling round
#
#        :attr:`python variable` default to None
#     '''
#     auto_jump_start = None
#     ''' invoked when auto-scroll is enabled to jump start before beginning
#             to apply restart_time time-frame rule
#     '''
#     prevent_many_jumps = None
#     ''' Once the auto jump start's attempted, this :attr:`prevent_many_jumps` ensures that there
#             will be no more jump start instead :attr:`restart_time` is utilized
#     '''
#     restart_time = NumericProperty(30)
#
#     def __init__(self, **kwargs):
#         super(AutoRollLabel, self).__init__(**kwargs)
#         self.animation_1 = None
#         self.animation_2 = None
#
#     def on_size(self, *largs):
#         root = App.get_running_app().root
#         if root.ready is not True:
#             return
#         self.re_order_schedules()
#
#     def on_children(self, *largs):
#         if largs[1]:
#             largs[1][0].bind(texture_size=self.on_texture_size)
#
#     def check_viewport_size(self, *largs):
#         if not self.size[0]:
#             return
#
#         child = self.children[0]
#         if child.size[0] > self.size[0]:
#             time_frame_const = 35 / 800  # Personal const based on self experience,calculation,observation..
#             initial_time = (self.size[0] * time_frame_const)
#             duration = (child.size[0] * initial_time / self.size[0])
#
#             if child.hovered and not self.autoScroll:
#                 self.ready_scroll(child.x, initial_time, duration)
#             elif self.autoScroll:
#                 start_at = 8 if not self.prevent_many_jumps else self.restart_time
#                 self.auto_jump_start = Clock.schedule_once(
#                     lambda x: self.ready_scroll(child.x, initial_time, duration), start_at)
#
#     def ready_scroll(self, *largs):
#         if self.auto_jump_start:
#             self.auto_jump_start = None
#             self.prevent_many_jumps = True
#
#         self.animation_1 = Animation(right=largs[0], d=largs[2])
#         self.animation_2 = Animation(x=0, d=largs[1])
#
#         self.animation_1.bind(on_complete=self.animation1_complete)
#         self.animation_2.bind(on_complete=self.animation2_complete)
#         self.animation_1.start(self.children[0])
#
#     def _restart_scroll(self, *largs):
#         if self.animation_1:
#             self.animation_1.start(self.children[0])
#
#     def on_texture_size(self, *largs):
#         largs[0].width = largs[1][0]
#         self.prevent_many_jumps = None
#         self.re_order_schedules()
#
#     def re_order_schedules(self):
#         self.cancel_schedules()
#         self.cancel_animations()
#
#         if self.autoScroll:
#             self.check_viewport_size()
#
#     def cancel_schedules(self):
#         if self.auto_jump_start:
#             self.auto_jump_start.cancel()
#             self.auto_jump_start = None
#
#         if self.scrollHandler:
#             self.scrollHandler.cancel()
#             self.scrollHandler = None
#
#     def cancel_animations(self):
#         child = self.children[0]
#         if self.animation_1:
#             self.animation_1.cancel(child)
#         if self.animation_2:
#             self.animation_2.cancel(child)
#
#         self.reset_viewport()
#
#     def animation1_complete(self, *largs):
#         largs[1].x = self.size[0]
#         self.animation_2.start(largs[1])
#
#     def animation2_complete(self, *largs):
#         if self.autoScroll:
#             self.scrollHandler = Clock.schedule_once(
#                 self._restart_scroll, self.restart_time)
#
#     def compute_restartTime(self, t_frame=None):
#         if t_frame is None:
#             self.restart_time = 30
#         else:
#             ratio = int(t_frame / 50)
#             if ratio < 3:
#                 if t_frame > 30:
#                     self.restart_time = t_frame
#                 return
#             if ratio > 10:
#                 ratio = int(t_frame / (50 * 9))
#             self.restart_time = t_frame / ratio
#
#     def on_enter(self):
#         if not self.autoScroll:
#             self.check_viewport_size()
#
#     def on_leave(self):
#         if not self.autoScroll:
#             self.cancel_animations()
#
#     def reset_viewport(self):
#         self.children[0].x = 0
#
#
# class CommonLabelButton(MyButton, HoverableLabel):
#     hoverClr = ListProperty([1, .8, 1, .1])


# class CustomButton(CommonLabelButton):
#     spared = NumericProperty(4)
#     h_normal = ListProperty([0, 0, 0, 0])
#     normal = ListProperty([1, 1, 1, 1])
#     radius = ListProperty([2])
#     source = StringProperty("")
#
#     def on_enter(self):
#         self.exchange_color()
#
#     def on_leave(self):
#         self.exchange_color()
#
#     def exchange_color(self):
#         if not self.hoverClr:
#             return
#
#         n, h = self.h_normal.copy(), self.hoverClr.copy()
#         self.h_normal, self.hoverClr = h, n
#
#
# class PlayItem(CommonLabelButton):
#     fileSource = StringProperty('')
#     source = StringProperty('Icons/thumbnail.png')
#     selected_normal = ListProperty([1, .3, 0, .1])
#     normal = ListProperty([0, 0, 0, 0])
#     hoverClr = ListProperty([0, 1, 0, .1])
#     selected = BooleanProperty(False)
#
#     def __init__(self, **kwargs):
#         super(PlayItem, self).__init__(**kwargs)
#         self.text = path.basename(self.fileSource)
#
#     def on_down(self):
#         if self.hovered and not self.selected:
#             self.on_leave()
#         self.selected = not self.selected
#         self.parent.on_new_focused(self)
#
#     def admit_focus(self):
#         self.selected = not self.selected
#         if self.hovered:
#             self.on_enter()
#
#     def on_enter(self):
#         self.exchange_color()
#
#     def on_leave(self):
#         self.exchange_color()
#
#     def exchange_color(self):
#         if self.selected:
#             return
#         n, h = self.normal.copy(), self.hoverClr.copy()
#         self.normal, self.hoverClr = h, n
#
#     def change_playing_color(self):
#         self.color = [.8, .2, 0, 1] if self.color == [.35, .35, .3, 1] else [.35, .35, .3, 1]


# class MainRoot(BoxLayer):
#     ready = None
#     '''
#     Represents the readiness of the main GUIs on start-up
#     '''
#     resizeLock = True
#     '''
#     Temporal permission lock when switching modes and changing window size
#         `It prevents window auto reshaping on resize while switching mode manually
#
#     :attr: is a :class:`<bool>` and default to None
#     '''
#     temp_pos = None
#     '''
#     Temporal position when changing window size manually
#     :attr: is a :class:`<list>` and default to None
#     '''
#     temp_dropped = None
#     '''
#     Temporal container for all being dropped files
#     :att:`temp_dropped` is a :class:`~<list>` and default to None
#     '''
#     dropping = None
#     '''
#     Automatic counter measure and activation while the dropping is in progress
#     '''
#
#     def __init__(self, **kwargs):
#         super(MainRoot, self).__init__(**kwargs)
#         self.ready = Clock.schedule_interval(self._getReady_, .1)
#
#     @staticmethod
#     def getProperty(prop_name):
#         return getProperty(prop_name)
#
#     def on_size(self, *largs):
#         if self.resizeLock is None:
#             self.update_left_nav_size(largs[1][0])
#
#     def update_left_nav_size(self, width):
#         # enforcing LeftNavMenu size restriction on window resize
#         if len(self.ids.msc_cont.children) > 1:
#             left_nav = self.ids.msc_cont.children[1]
#             left_nav.max_size = width - 450
#
#     def playlist_fromCLI(self, *largs):
#         print(largs)  # Capture all inputs from command line on startup
#
#     def _getReady_(self, *largs):
#         if self.ids:
#             # cancelling the auto checkup and confirming readiness
#             self.ready.cancel()
#             self.ready = True
#             # positioning window on startup
#             startUp_window_pos()
#             # turning volume and media progress bars interacting
#             self.ids.play3GUIs.add_progressBars_listeners()
#             # listening to mouse position relative to window so to set custom keypad
#             self.add_window_cursor_listeners()
#             # enabling auto view mode switch on window resize
#             self.resizeLock = None
#             self.enable_dropFile()
#
#     def add_window_cursor_listeners(self):
#         play3 = self.ids.play3GUIs
#         Window.bind(on_cursor_enter=play3.on_enter, on_cursor_leave=play3.on_leave)
#
#     def remove_window_cursor_listeners(self):
#         play3 = self.ids.play3GUIs
#         Window.unbind(on_cursor_enter=play3.on_enter, on_cursor_leave=play3.on_leave)
#
#     def enable_dropFile(self):
#         Window.bind(on_dropfile=self.on_file_dropped)
#
#     def on_file_dropped(self, *largs):
#         if self.dropping is None:
#             # mapping a dropping status widget
#             self.show_dropping_status()
#             # creating after dropping counter measure
#             self.dropping = Clock.schedule_once(self.after_all_dropped, 1.4)
#         # freezing after dropping counter measure just to sort a dropped file
#         self.dropping.cancel()
#         # decoding dropped file to <class str>
#         dropped_file = largs[1].decode('utf-8')
#         self.verify_file_address(dropped_file)
#         # unfreeze after dropping counter measure
#         self.dropping()
#
#     def after_all_dropped(self, *largs):
#         # clearing the auto measure after dropping for a fresh start
#         self.dropping = None
#
#         # ensure that :attr:`temp_dropped` is an empty list
#         if not self.temp_dropped:
#             self.temp_dropped = None
#             self.remove_dropping_status()
#             return
#
#         # swapping temp_dropped to another container so that it can be wiped clean
#         copyOf_dropped = self.temp_dropped
#         # wiping clean temp_dropped container for a fresh start
#         self.temp_dropped = None
#         # retrieving playlists container
#         playlists_manager = self.ensure_existenceOf_leftNav()
#         # making some decision on a new coming list content of where to put them
#         playlists_manager._decisionOn_newList(copyOf_dropped)
#
#     def verify_file_address(self, address):
#         if not path.exists(address):
#             return
#
#         # the address points to a folder
#         if path.isdir(address):
#             # listing its contents
#             contents = listdir(address)
#             # checking if contents exist, if so, add the address to the temp_dropped
#             if contents:
#                 self.initiate_temp_dropped()
#                 self.temp_dropped.append(address)
#             else:
#                 return
#
#         # the address points to file
#         elif path.isfile(address):
#             # reading accepted file formats from settings file
#             formats = json.loads(SETTINGS.get('MEDIA', 'formats'))
#             # getting the file format
#             format_index = address.rsplit('.', 1)[-1]
#             # checking if the file format is compatible with accepted ones
#             # if so, add the address to the temp_dropped
#             if format_index.lower() in formats:
#                 self.initiate_temp_dropped()
#                 self.temp_dropped.append(address)
#             else:
#                 return
#
#     def disable_dropFile(self):
#         # disabling file dropping capability
#         Window.unbind(on_dropfile=self.on_file_dropped)
#
#     def show_dropping_status(self):
#         loading = LoadingStatus(
#             padding=(0, 5), size_hint_x=None, width=55)
#         self.ids.head_bar.ids.posterOffice.add_widget(loading, 2)
#
#     def remove_dropping_status(self):
#         poster = self.ids.head_bar.ids.posterOffice
#         poster.remove_widget(poster.children[2])
#
#     def initiate_temp_dropped(self):
#         '''
#         invoked when trying to initiate :attr:`temp_dropped` for the first use
#         :return:
#         '''
#
#         if self.temp_dropped is None:
#             self.temp_dropped = []
#
#     def ensure_existenceOf_leftNav(self):
#         '''
#         It's to be used when adding dropped files to the playlist widget
#             located on the LeftNavMenu widget
#         :return:`left-nav` is a :class:`~kivy.property.ObjectProperty` and contains LeftNavMenu
#         '''
#         return self.ids.head_bar.ensure_existenceOf_leftNav()
#
#
# class VideoAudioPlayer(Screen):
#     # An engine for audio medias
#     _audioModular = ObjectProperty(None, allownone=True)
#     # An engine for video medias
#     _videoModular = ObjectProperty(None, allownone=True)
#     # A threaded cpu-clock for reading current position audio playing media
#     _audioPositionThread = None
#     # current loaded media source file
#     _source = StringProperty('')
#     # default volume of media player
#     _volume = NumericProperty(0.5)
#     # Position value to jump to while the media is in play or pause state
#     _seek_pos = NumericProperty(None, allownone=True)
#     # Estimated media lasting period
#     _duration = NumericProperty(None, allownone=True)
#     # Current elapsed time-frame of the media
#     _current_pos = NumericProperty(None, allownone=True)
#     # media player functioning status
#     _state = OptionProperty('stop', options=['stop', 'play', 'pause'])
#     # Repeating feature status of the media player
#     _loop = OptionProperty('none', options=['none', 'one', 'all'])
#     # randomizing status of the media player
#     _shuffle = BooleanProperty(False)
#     # identifier for intentional cease of media functionality
#     _forcedStop = BooleanProperty(False)
#     _nextIndex = NumericProperty(None, allownone=True)
#     _currentIndex = NumericProperty(None, allownone=True)
#     prevent_play_another = None
#     _keypadInterface = None
#
#     def on_enter(self, window):
#         """ When mouse enters player, invoke acquire keypad and invoke keypad control directive protocol """
#         try:
#             self._keypadInterface = window.request_keyboard(self._keypadInterface_detached, self)
#             self._keypadInterface.bind(on_key_down=self._command_media_directives_with_keypad_)
#         except Exception as exc:
#             logger.error_(f'Failed to acquire keyboard due to {exc}')
#             # -- snippets -- to inform user that keypad directives are not available
#
#     def on_leave(self, window=None):
#         """ When mouse leaves player, release keypad interface, and disengage keypad control directive protocol """
#         try:
#             if self._keypadInterface:
#                 self._keypadInterface.unbind(on_key_down=self._command_media_directives_with_keypad_)
#                 self._keypadInterface = None
#         except Exception as exc:
#             logger.error_(
#                 f'''Failed to detach keypad-interface due to {exc}
#                     Deploying keypadInterface detaching countermeasure protocol
#                 '''
#             )
#             self.on_leave()
#
#     def _command_media_directives_with_keypad_(self, interface, keyCode, character, modifier):
#         """ keypad directives for commanding media player """
#
#         if character == 's':
#             self.stop_playback()
#         elif character == 'n':
#             self._next()
#         elif character == 'p':
#             self._previous()
#         elif character == 'l':
#             self._loop_alter(self.ids.loope)
#         elif character == 'm':
#             self._volume_tuning_keypad_directive('mute')
#         elif character == 'r':
#             self._shuffle_alter(self.ids.shufflee)
#         elif character == 'e':
#             self.headBar_hypothesis('mini')
#         elif character == 'd':
#             self.headBar_hypothesis('dock')
#         elif character == 'f':
#             self.headBar_hypothesis('full')
#         elif character == 'q':
#             self.headBar_hypothesis('quit')
#         elif keyCode[1] == 'spacebar':
#             self.play_pause(self.ids.pp)
#         elif keyCode[1] == 'up' and 'ctrl' in modifier:
#             self._volume_tuning_keypad_directive('up')
#         elif keyCode[1] == 'down' and 'ctrl' in modifier:
#             self._volume_tuning_keypad_directive('down')
#         elif keyCode[1] == 'left' and 'shift' in modifier:
#             self.backward_wind()
#         elif keyCode[1] == 'right' and 'shift' in modifier:
#             self.forward_wind()
#
#     def _keypadInterface_detached(self):
#         """ After the keypad has served its purpose, it gets released to reduce memory allocated """
#         pass
#
#     def _volume_tuning_keypad_directive(self, action):
#         """ Volume regulation analysis based on keypad directive """
#
#         volumeTuner = self.ids.volTuner
#         if action == 'up':
#             volumeScale = volumeTuner.level + (volumeTuner.size[0] * .05)
#         elif action == 'down':
#             volumeScale = volumeTuner.level - (volumeTuner.size[0] * .05)
#         elif action == 'mute':
#             self._mute()
#             return
#
#         if volumeScale < 0:
#             volumeScale = 10e-24
#         elif volumeScale > volumeTuner.width:
#             volumeScale = volumeTuner.width
#         volumeTuner.level = volumeScale
#
#     @staticmethod
#     def _size_modulation_keypad_directive(action):
#         """ Resizing analysis of keypad directive """
#
#         if action == 'F':
#             pass
#         elif action == 'E':
#             pass
#         elif action == 'D':
#             pass
#         elif action in ('Q', 'ESC'):
#             pass
#
#     def _isMediaLoaded(self, state=None):
#         """ To find out if player is ready to read loaded media source """
#         return self._audioModular or self._videoModular
#
#     def playing_request_from_(self, source, index):
#         """ Communication stream from playlists to player """
#
#         if self._source:
#             self.prevent_play_another = True
#             self.apply_stop()
#         # assign current media source index from its container
#         self._currentIndex = self._nextIndex = index
#         # media source address to load its data
#         self._source = source
#
#     def on_source(self, interface, new_source):
#         """ A trigger when player source path changes """
#
#         if not new_source:
#             return
#         self._player_prepping_routine(new_source, is_supported_format(new_source))
#
#     def _player_prepping_routine(self, media_source, modular):
#         """ decides on which rightful modular to use given the format of media_source """
#         pass
#
#     def on_volume(self, interface, intensity):
#         """ A trigger to apply volume compliance when changes occur """
#
#         if self._audioModular:
#             self._audioModular.volume = intensity
#         elif self._videoModular:
#             self._videoModular.volume = interface
#
#     def on_state(self, interface, status):
#         """ A trigger to invoke certain protocols when changes occur to player state """
#         pass
#
#     def on_seek_pos(self, interface, jump_to):
#         """  triggers certain protocols when changes occur """
#
#         if jump_to is None:
#             return
#         if self._videoModular:
#             pass
#         if self._audioModular:
#             pass
#         # After certain protocols have completed their routines, reset this value default
#         self._seek_pos = None
#
#     def on_duration(self, interface, lifetime):
#         """ triggers protocols for updating-UI when changes occur """
#
#         if lifetime is None:
#             return
#
#     def on_current_pos(self, interface, pos_at):
#         """ triggers protocols for UI-updating when changes occur """
#
#         if pos_at is None:
#             return
#
#     def _manual_duration_getter_for_audios(self):
#         """ cpu-clocked targeted for retrieving playing media duration lifetime value
#             And more, initiates a threaded cpu-clock getter for current position
#             This applies only on audio medias
#         """
#
#         media_duration = duration_getter(self.source)
#         if (media_duration <= 0) or (type(media_duration) is not float):
#             Clock.schedule_once(lambda *largs: self._manual_duration_getter_for_audios(), .28)
#         else:
#             self.duration = media_duration
#             self._audioPositionThread = Thread(
#                 target=Clock.schedule_interval,
#                 args=(self._manual_pos_getter_for_audios, .48)).start()
#
#     def _manual_pos_getter_for_audios(self, *largs):
#         current_pos = self._audioModular.get_pos()
#         self.current_pos = 0 if current_pos < 0 else current_pos
#
#     def on_modular_state(self, modular, status):
#         """ triggers certain routines when such Modular state changes """
#
#         if status == 'play':
#             pass
#         elif status == 'pause':
#             pass
#         else:
#             pass
#
#     def _stopping_routine(self):
#         """ collective actions to be carried out if player is to stop reading operations """
#         pass
#
#     def _pausing_routine(self):
#         """ collective actions to be carried out if player is to freeze reading operations """
#         pass
#
#     def _playing_routine(self):
#         """ certain changes and updates to be applied when player enters reading operations """
#         pass
#
#     def _resuming_routine(self):
#         """ Bunch of actions to be carried out when resuming player operations """
#         pass
#
#     def _resuming_audio_sub_routine(self):
#         """ Other necessary key changes to make when resuming audio media """
#
#         self._audioModular.volume = 0
#         # self.state = 'play'
#         # self.resume()
#         # self.ids.pp.source = 'Icons/pause.png'
#
#     def _player_resetting_routine(self):
#         """ reset player to default means undo all changes made to it or in its behalf """
#         pass
#
#     def _nextInline_to_play_routine(self):
#         """ decides on whether player should continues its operations or not """
#         pass
#
#     def _clear_modularTriggers(self):
#         """ clears changes-observers to modular attributes """
#         pass
#
#     def _create_modularTriggers(self):
#         """ adds changes-observers to modular attributes """
#         pass
#
#     def _create_playerProgress_levelTriggers(self):
#         """ adds changes-triggers to progress bars of the players """
#         pass
#
#     def pauseAndPlay_(self, interface):
#         """ motion event of pause and play interface-actors """
#         pass
#
#     def stop_(self, interface):
#         """ motion events of stop interface-actor """
#         pass
#
#     def forward_(self, interface):
#         """ motion events of forward interface-actor """
#         pass
#
#     def backward_(self, interface):
#         """ motion events of backward interface-actor """
#         pass
#
#     def next_(self, interface):
#         """ motion events of next interface-actor """
#         pass
#
#     def previous_(self, interface):
#         """ motion events of previous interface-actor """
#         pass
#
#     def loop_(self, interface):
#         """ motion events of loop interface-actor """
#         pass
#
#     def shuffle_(self, interface):
#         """ motion events of shuffle interface-actor """
#         pass


class Recorder(Screen):
    pass


class ImageViewer(Screen):
    pass


class BroadcastPlayer(Screen):
    pass


class Downloader(Screen):
    pass


class Splashing(BoxLayout):
    pass
