import sonos_manager
import re as re
from functools import lru_cache 

MENU_PAGE_SIZE = 6

# Screen render types
MENU_RENDER_TYPE = 0
NOW_PLAYING_RENDER = 1
SEARCH_RENDER = 2

# Menu line item types
LINE_NORMAL = 0
LINE_HIGHLIGHT = 1
LINE_TITLE = 2

class LineItem():
    def __init__(self, title = "", line_type = LINE_NORMAL, show_arrow = False):
        self.title = title
        self.line_type = line_type
        self.show_arrow = show_arrow

class Rendering():
    def __init__(self, type):
        self.type = type

    def unsubscribe(self):
        pass

class MenuRendering(Rendering):
    def __init__(self, header = "", lines = [], page_start = 0, total_count = 0):
        super().__init__(MENU_RENDER_TYPE)
        self.lines = lines
        self.header = header
        self.page_start = page_start
        self.total_count = total_count
        self.now_playing = sonos_manager.DATASTORE.now_playing
        self.has_internet = sonos_manager.has_internet

class NowPlayingRendering(Rendering):
    def __init__(self):
        super().__init__(NOW_PLAYING_RENDER)
        self.callback = None
        self.after_id = None

    def subscribe(self, app, callback):
        if callback == self.callback:
            return
        new_callback = self.callback is None
        self.callback = callback
        self.app = app
        if new_callback:
            self.refresh()

    def refresh(self):
        if not self.callback:
            return
        if self.after_id:
            self.app.after_cancel(self.after_id)
        self.callback(sonos_manager.DATASTORE.now_playing)
        self.after_id = self.app.after(500, lambda: self.refresh())

    def unsubscribe(self):
        super().unsubscribe()
        self.callback = None
        self.app = None

class NowPlayingCommand():
    def __init__(self, runnable = lambda:()):
        self.has_run = False
        self.runnable = runnable
    
    def run(self):
        self.has_run = True
        self.runnable()

class NowPlayingPage():
    def __init__(self, previous_page, header, command):
        self.has_sub_page = False
        self.previous_page = previous_page
        self.command = command
        self.header = header
        self.live_render = NowPlayingRendering()
        self.is_title = False

    def play_previous(self):
        sonos_manager.play_previous()
        self.live_render.refresh()

    def play_next(self):
        sonos_manager.play_next()
        self.live_render.refresh()

    def toggle_play(self):
        sonos_manager.toggle_play()
        self.live_render.refresh()

    def nav_prev(self):
        sonos_manager.run_async(lambda: self.play_previous()) 

    def nav_next(self):
        sonos_manager.run_async(lambda: self.play_next()) 

    def nav_play(self):
        sonos_manager.run_async(lambda: self.toggle_play()) 

    def nav_up(self):
        pass

    def nav_down(self):
        pass

    def nav_select(self):
        return self

    def nav_back(self):
        return self.previous_page

    def render(self):
        if (not self.command.has_run):
            self.command.run()
        return self.live_render

EMPTY_LINE_ITEM = LineItem()
class MenuPage():
    def __init__(self, header, previous_page, has_sub_page, is_title = False):
        self.index = 0
        self.page_start = 0
        self.header = header
        self.has_sub_page = has_sub_page
        self.previous_page = previous_page
        self.is_title = is_title

    def total_size(self):
        return 0

    def page_at(self, index):
        return None

    def nav_prev(self):
        sonos_manager.run_async(lambda: sonos_manager.play_previous()) 

    def nav_next(self):
        sonos_manager.run_async(lambda: sonos_manager.play_next()) 

    def nav_play(self):
        sonos_manager.run_async(lambda: sonos_manager.toggle_play()) 
    
    def get_index_jump_up(self):
        return 1

    def get_index_jump_down(self):
        return 1

    def nav_up(self):
        jump = self.get_index_jump_up()
        if(self.index >= self.total_size() - jump):
            return
        if (self.index >= self.page_start + MENU_PAGE_SIZE - jump):
            self.page_start = self.page_start + jump
        self.index = self.index + jump

    def nav_down(self):
        jump = self.get_index_jump_down()
        if(self.index <= (jump - 1)):
            return
        if (self.index <= self.page_start + (jump - 1)):
            self.page_start = self.page_start - jump
            if (self.page_start == 1):
                self.page_start = 0
        self.index = self.index - jump

    def nav_select(self):
        return self.page_at(self.index)

    def nav_back(self):
        return self.previous_page

    def render(self):
        lines = []
        total_size = self.total_size()
        for i in range(self.page_start, self.page_start + MENU_PAGE_SIZE):
            if (i < total_size):
                page = self.page_at(i)
                if (page is None) :
                    lines.append(EMPTY_LINE_ITEM)
                else:
                    line_type = LINE_TITLE if page.is_title else \
                        LINE_HIGHLIGHT if i == self.index else LINE_NORMAL
                    lines.append(LineItem(page.header, line_type, page.has_sub_page))
            else:
                lines.append(EMPTY_LINE_ITEM)
        return MenuRendering(lines=lines, header=self.header, page_start=self.index, total_count=total_size)

class PlaceHolderPage(MenuPage):
    def __init__(self, header, previous_page, has_sub_page=True, is_title = False):
        super().__init__(header, previous_page, has_sub_page, is_title)

class RootPage(MenuPage):
    def __init__(self, previous_page):
        super().__init__("Sonos Pod", previous_page, has_sub_page=True)
        self.pages = [
            NowPlayingPage(self, "Now Playing", NowPlayingCommand())
        ]
        self.index = 0
        self.page_start = 0
    
    def get_pages(self):
        return self.pages
    
    def total_size(self):
        return len(self.get_pages())

    def page_at(self, index):
        return self.get_pages()[index]


