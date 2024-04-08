import os

from bs4 import BeautifulSoup

from kivy.config import Config

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard


__version__ = '0.1 alpha'


class ResultScreen(Screen):
    input_data = ObjectProperty()

    def update_text_input(self, data):
        self.input_data.text += '\n' + data

    def get_back_and_clean(self, results):
        self.input_data.text = ''
        self.manager.current = 'ShortInfo'

    def copy_results(self):
        text = self.input_data.text
        Clipboard.copy(text)


class CustomPopup(Popup):
    error_info = ObjectProperty()

    def update_content(self, data):
        if len(data) < 1:
            data = '\n --Пустая строка--'
        elif len(data) > 1 and data[-4:] not in ('html', '.htm'):
            data = '\nРасширение файла не поддерживается программой.'
        elif 1 < len(data) <= 30:
            data = f'\n {data[-30:]}'
        else:
            data = f'\n ... {data[-30:]}'
        self.error_info.text = (
            'Указанный путь не найден, проверьте данные: ' +
            f'{data}')


class ShortInfo(Screen):
    def __init__(self, **var_args):
        super(ShortInfo, self).__init__(**var_args)
        Window.size = (840, 440)
        Config.set('graphics', 'resizable', False)
        Config.write()

    def open_file(self, data: str):
        try:
            file_path = os.path.relpath(data)
            with open(file_path, 'r') as f:
                html = BeautifulSoup(f.read(), 'lxml')
            return self.parse_html(html)
        except (FileNotFoundError, ValueError):
            return self.send_error_msg(data)

    def send_error_msg(self, data):
        popup = CustomPopup()
        popup.update_content(data)
        popup.open()

    def parse_html(self, html):
        table = html.find_all('table')
        trs = []
        for td in table:
            trs.append(td.find_all('tr'))
        report_title = html.title.text
        report_date = trs[3][11].text
        name_pc = trs[3][8].text
        name_user_report = trs[3][9].text
        monitor = trs[3][25].text
        oc = trs[3][3].text
        cpu = trs[3][14].text
        motherboard = trs[3][15].text
        videoadapter = trs[3][22].text
        memory = trs[3][17].text
        self.manager.current = 'ResultScreen'
        self.manager.get_screen('ResultScreen').update_text_input(report_title)
        self.manager.get_screen('ResultScreen').update_text_input(report_date)
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
