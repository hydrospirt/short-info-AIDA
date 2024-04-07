import os

from bs4 import BeautifulSoup

from kivy.config import Config

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

__version__ = '0.1'


class CustomPopup(Popup):
    pass


class ShortInfo(GridLayout):
    def __init__(self, **var_args):
        super(ShortInfo, self).__init__(**var_args)
        Window.size = (840, 440)
        Config.set('graphics', 'resizable', False)
        Config.write()

    def open_file(self, data: str):
        if not data:
            return self.send_error_msg(data)
        with open(os.path.relpath(data), 'r') as f:
            html = BeautifulSoup(f.read(), 'html.parser')
        return html

    def send_error_msg(self, data):
        popup = CustomPopup()
        popup.open()

    def parse_html(self, html):
        ...


class ShortInfoApp(App):
    def build(self):
        self.title = f'Short Info AIDA v{__version__}'
        self.icon = 'assets/icon/icon.png'
        self.play_music()
        return ShortInfo()

    def play_music(self):
        sound_loader = SoundLoader.load('assets/sound/At_Dooms_Gate.mp3')
        sound_loader.loop = True
        if sound_loader:
            sound_loader.play()


if __name__ == '__main__':
    ShortInfoApp().run()
