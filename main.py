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
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

__version__ = '0.1 alpha'


class ResultScreen(Screen):
    def __init__(self, **kwargs):
        super(ResultScreen, self).__init__(**kwargs)
        self.gird = GridLayout(cols=1)
        self.text_input = TextInput(size=(400, 400))
        self.copy_btn = Button(text='Скопировать')
        self.back_btn = Button(text='Вернуться')
        self.add_widget(self.gird)
        self.gird.add_widget(self.text_input)
        self.gird.add_widget(self.copy_btn)
        self.gird.add_widget(self.back_btn)

    def update_text_input(self, data):
        self.text_input.text += '\n' + data


class CustomPopup(Popup):
    pass


class ShortInfo(Screen):
    def __init__(self, **var_args):
        super(ShortInfo, self).__init__(**var_args)
        Window.size = (840, 440)
        Config.set('graphics', 'resizable', False)
        Config.write()

    def open_file(self, data: str):
        if not data:
            return self.send_error_msg(data)
        with open(os.path.relpath(data), 'r') as f:
            html = BeautifulSoup(f.read(), 'lxml')
        return self.parse_html(html)

    def send_error_msg(self, data):
        popup = CustomPopup()
        popup.open()

    def parse_html(self, html):
        table = html.find_all('table')
        trs = []
        for td in table:
            trs.append(td.find_all('tr'))
        report_title = html.title.text
        report_date = trs[3][11].text
        name_pc = trs[3][8].text
        print(name_pc)
        name_user_report = trs[3][9].text
        monitor = trs[3][25].text
        oc = trs[3][3].text
        cpu = trs[3][14].text
        motherboard = trs[3][15].text
        videoadapter = trs[3][22].text
        memory = trs[3][17].text
        self.manager.current = 'ResultScreen'
        self.manager.get_screen('ResultScreen').update_text_input(report_title)
        self.manager.get_screen('ResultScreen').update_text_input(monitor)


class ShortInfoApp(App):
    def build(self):
        self.title = f'Short Info AIDA v{__version__}'
        self.icon = 'assets/icon/icon.png'
        # self.play_music()
        sm = ScreenManager()
        sm.add_widget(ShortInfo(name='ShortInfo'))
        sm.add_widget(ResultScreen(name='ResultScreen'))
        return sm

    def play_music(self):
        sound_loader = SoundLoader.load('assets/sound/At_Dooms_Gate.mp3')
        sound_loader.loop = True
        if sound_loader:
            sound_loader.play()


if __name__ == '__main__':
    ShortInfoApp().run()
