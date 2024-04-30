import os
import sys
import io

from bs4 import BeautifulSoup

from kivy.resources import resource_add_path, resource_find

from kivy.config import Config

from kivymd.app import MDApp
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.clipboard import Clipboard


__version__ = '0.1 alpha'

TITLE = f'Short Info AIDA v{__version__}'

FILE_MUSIC = 'assets/sound/At_Dooms_Gate.mp3'
ICON_ASSET = 'assets/icon/icon.png'

EXT_FILE = ('html', '.htm')

ERR_EMPTY_LINE = '\n --Пустая строка--'
ERR_WRONG_EXT = '\nРасширение файла не поддерживается программой.'
ERR_MSG_TXT = 'Указанный путь не найден, проверьте данные: '


class CInfo:
    CNAME = 'Имя компьютера'
    UNAME = 'Имя пользователя'
    CPTYPE = 'Тип ЦП'
    CPUIDNAME = 'Имя ЦП CPUID'
    MOTHERB = 'Системная плата'
    RAM = 'Системная память'
    RSIZE = 'Размер модуля'
    RSPEED = 'Скорость памяти'
    VIDEOA = 'Видеоадаптер'
    MONITOR = 'Монитор'
    DISKDRIVE = 'Дисковый накопитель'
    TVOLUME = 'Общий объём'
    PRINTER = 'Принтер'
    TDATE = 'Дата / Время'
    OS = 'Операционная система'
    USB = 'USB'


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
        if obj.icon == 'stop':
            self.music.play()
            self.toggle_icon.icon = 'play'
        else:
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
            if CInfo.CNAME in tag.get_text():
                label_aida = tag.get_text()
                pc_name = tag.find_next_sibling().get_text()
                sum_pc_name = label_aida + pc_name
                info_pc_data.append(sum_pc_name)
            if CInfo.UNAME in tag.get_text():
                label_aida = tag.get_text()
                user_name = tag.find_next_sibling().get_text()
                sum_user_name = label_aida + user_name
                info_pc_data.append(sum_user_name)
            if CInfo.CPTYPE in tag.get_text():
                processor = tag.find_next_sibling().get_text()
                processor = processor.rstrip()
                if len(processor) < 30:
                    new_td_tags = tables[9].find_all('td')
                    for tag in new_td_tags:
                        if CInfo.CPUIDNAME in tag.get_text():
                            processor = tag.find_next_sibling().get_text()
                            processor = processor.rstrip()
                if processor not in pc_data:
                    pc_data.append(processor)
            if CInfo.MOTHERB in tag.get_text():
                try:
                    motherboard = tag.find_next_sibling().get_text()
                    motherboard = motherboard.rstrip()
                    pc_data.append(motherboard)
                except AttributeError:
                    ...
            if CInfo.RAM in tag.get_text():
                new_td_tags = tables[25].find_all('td')
                pc_memory = ''
                for tag in new_td_tags:
                    if CInfo.RSIZE in tag.get_text():
                        size_memory = tag.find_next_sibling().get_text()
                        size_memory = size_memory.rstrip()
                        size_memory = size_memory.split()
                        size_memory = f'{size_memory[0]} {size_memory[1]}'
                        pc_memory += f' {size_memory}'
                    if CInfo.RSPEED in tag.get_text():
                        spd_memory = tag.find_next_sibling().get_text()
                        spd_memory = spd_memory.rstrip()
                        pc_memory += f' {spd_memory}'
                pc_data.append(pc_memory)
            if CInfo.VIDEOA in tag.get_text():
                videoadapter = tag.find_next_sibling().get_text()
                videoadapter = videoadapter.rstrip()
                if videoadapter not in pc_data:
                    pc_data.append(videoadapter)
            if CInfo.MONITOR in tag.get_text():
                label_aida = tag.get_text()
                monitor = tag.find_next_sibling().get_text()
                sum_monitor = label_aida + monitor
                info_pc_data.append(sum_monitor)
            if CInfo.DISKDRIVE in tag.get_text():
                disk = tag.find_next_sibling().get_text()
                if CInfo.USB not in disk:
                    disk = disk.rstrip()
                    pc_data.append(disk)
            if CInfo.TVOLUME in tag.get_text():
                disk_free_space = tag.find_next_sibling().get_text()
                disk_free_space = disk_free_space.rstrip()
                pc_data.append(disk_free_space)
            if CInfo.PRINTER in tag.get_text():
                label_aida = tag.get_text()
                printer = tag.find_next_sibling().get_text()
                if printer.rstrip() not in ('Adobe PDF',
                                            'Fax',
                                            'Microsoft Print to PDF',
                                            'Microsoft XPS Document Writer',
                                            'OneNote'):
                    sum_printer = label_aida + printer
                    info_pc_data.append(sum_printer)
            if CInfo.TDATE in tag.get_text():
                label_aida = tag.get_text()
                date_and_time = tag.find_next_sibling().get_text()
                sum_dt = label_aida + date_and_time
                info_pc_data.append(sum_dt)
            if CInfo.OS in tag.get_text():
                oc = tag.find_next_sibling().get_text()
                oc = oc.rstrip()
        pc_data.append(oc)

        report_title = html.title.text
        self.manager.current = 'ResultScreen'
        self.manager.get_screen(
            'ResultScreen').update_text_input(report_title)
        self.manager.get_screen(
            'ResultScreen').update_text_input(''.join(info_pc_data))
        self.manager.get_screen(
            'ResultScreen').update_text_input('\\'.join(pc_data))


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
            data = ERR_EMPTY_LINE
        elif len(data) > 1 and data[-4:] not in EXT_FILE:
            data = ERR_WRONG_EXT
        elif 1 < len(data) <= 30:
            data = f'\n {data[-30:]}'
        else:
            data = f'\n ... {data[-30:]}'
        self.error_info.text = (
            ERR_MSG_TXT + f'{data}')


class ShortInfoApp(MDApp):
    def build(self):
        self.title = TITLE
        self.icon = ICON_ASSET
        sm = ScreenManager()
        sm.add_widget(ShortInfo(name='ShortInfo'))
        sm.add_widget(ResultScreen(name='ResultScreen'))
        return sm


if __name__ == '__main__':
    from kivymd.icon_definitions import md_icons # noqa
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    ShortInfoApp().run()
