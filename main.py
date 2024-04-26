import os
import io

from bs4 import BeautifulSoup

from kivy.config import Config

from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard


__version__ = '0.1 alpha'

FILE_MUSIC = 'assets/sound/At_Dooms_Gate.mp3'


class ShortInfo(Screen):
    toggle_icon = ObjectProperty()

    def __init__(self, **var_args):
        super(ShortInfo, self).__init__(**var_args)
        Window.size = (840, 440)
        Config.set('graphics', 'resizable', False)
        Config.write()
        self.music = SoundLoader.load(FILE_MUSIC)
        self.music.loop = True

    def toggle_music(self, obj):
        print(obj.icon)
        print(self.toggle_icon.icon)
        if obj.icon == 'stop':
            print('Music Playing')
            self.music.play()
            self.toggle_icon.icon = 'play'
        else:
            print('Music Playing')
            self.music.stop()
            self.toggle_icon.icon = 'stop'

    def open_file(self, data: str):
        try:
            file_path = os.path.abspath(data)
            with io.open(file_path, 'rb') as f:
                html = BeautifulSoup(f.read(), 'lxml')
            return self.parse_html(html)
        except (FileNotFoundError,  PermissionError, OSError):
            return self.send_error_msg(data)

    def send_error_msg(self, data):
        popup = CustomPopup()
        popup.update_content(data)
        popup.open()

    def parse_html(self, html):
        tables = html.find_all('table')
        td_tags = tables[3].find_all('td')

        info_pc_data = []
        pc_data = []

        for tag in td_tags:
            if 'Имя компьютера' in tag.get_text():
                label_aida = tag.get_text()
                pc_name = tag.find_next_sibling().get_text()
                sum_pc_name = label_aida + pc_name
                info_pc_data.append(sum_pc_name)
            if 'Имя пользователя' in tag.get_text():
                label_aida = tag.get_text()
                user_name = tag.find_next_sibling().get_text()
                sum_user_name = label_aida + user_name
                info_pc_data.append(sum_user_name)
            if 'Тип ЦП' in tag.get_text():
                processor = tag.find_next_sibling().get_text()
                processor = processor.rstrip()
                pc_data.append(processor)
            if 'Системная плата' in tag.get_text():
                try:
                    motherboard = tag.find_next_sibling().get_text()
                    motherboard = motherboard.rstrip()
                    pc_data.append(motherboard)
                except AttributeError:
                    ...
            if 'Видеоадаптер' in tag.get_text():
                videoadapter = tag.find_next_sibling().get_text()
                videoadapter = videoadapter.rstrip()
                if videoadapter not in pc_data:
                    pc_data.append(videoadapter)
            if 'Монитор' in tag.get_text():
                label_aida = tag.get_text()
                monitor = tag.find_next_sibling().get_text()
                sum_monitor = label_aida + monitor
                info_pc_data.append(sum_monitor)
            if 'Дисковый накопитель' in tag.get_text():
                disk = tag.find_next_sibling().get_text()
                if 'USB' not in disk:
                    disk = disk.rstrip()
                    pc_data.append(disk)
            if 'Общий объём' in tag.get_text():
                disk_free_space = tag.find_next_sibling().get_text()
                disk_free_space = disk_free_space.rstrip()
                pc_data.append(disk_free_space)
            if 'Принтер' in tag.get_text():
                label_aida = tag.get_text()
                printer = tag.find_next_sibling().get_text()
                if printer.rstrip() not in ('Adobe PDF', 'Fax', 'Microsoft Print to PDF', 'Microsoft XPS Document Writer', 'OneNote'):
                    sum_printer = label_aida + printer
                    info_pc_data.append(sum_printer)
            if 'Дата / Время' in tag.get_text():
                label_aida = tag.get_text()
                date_and_time = tag.find_next_sibling().get_text()
                sum_dt = label_aida + date_and_time
                info_pc_data.append(sum_dt)
            if 'Операционная система' in tag.get_text():
                oc = tag.find_next_sibling().get_text()
                oc = oc.rstrip()
        pc_data.append(oc)

        report_title = html.title.text
        self.manager.current = 'ResultScreen'
        self.manager.get_screen('ResultScreen').update_text_input(report_title)
        self.manager.get_screen('ResultScreen').update_text_input(''.join(info_pc_data))
        self.manager.get_screen('ResultScreen').update_text_input('\\'.join(pc_data))


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


class ShortInfoApp(MDApp):
    def build(self):
        self.title = f'Short Info AIDA v{__version__}'
        self.icon = 'assets/icon/icon.png'
        sm = ScreenManager()
        sm.add_widget(ShortInfo(name='ShortInfo'))
        sm.add_widget(ResultScreen(name='ResultScreen'))
        return sm


if __name__ == '__main__':
    ShortInfoApp().run()
