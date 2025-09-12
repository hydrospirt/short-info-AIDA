import io
import os
import re
import sys
from urllib.parse import unquote

from bs4 import BeautifulSoup
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.resources import resource_add_path
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserController
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp

__version__ = '0.2 alpha'
TITLE = f'Short Info AIDA v{__version__}'
PARSER = 'lxml'
FILE_MUSIC = 'assets/sound/At_Dooms_Gate.mp3'
ICON_ASSET = 'assets/icon/icon.png'
EXT_FILE = ('.html', '.htm')

# Сообщения об ошибках
ERR_EMPTY_LINE = '\n --Пустая строка--'
ERR_WRONG_EXT = '\nРасширение файла не поддерживается программой.'
ERR_MSG_TXT = 'Указанный путь не найден, проверьте данные: '


class CInfo:
    # Списки поддерживают оба языка: [русский, английский]
    CNAME = ['Имя компьютера', 'Computer Name']
    UNAME = ['Имя пользователя', 'User Name']
    CPTYPE = ['Тип ЦП', 'CPU Type']
    MOTHERB = ['Системная плата', 'Motherboard']
    VIDEOA = ['Видеоадаптер', 'Display Adapter']
    TDATE = ['Дата / Время', 'Date / Time']
    OS = ['Операционная система', 'Operating System']
    RSIZE = ['Размер модуля', 'Module Size']
    RTYPE = ['Тип памяти', 'Memory Type']
    RSPEED = ['Скорость памяти', 'Memory Speed']
    RAM_TOTAL = ['Системная память', 'System Memory']
    DISK_DRIVE = ['Дисковый накопитель', 'Disk Drive']
    PRINTER = ['Принтер', 'Printer']
    MAC_ADDRESS = ['Аппаратный адрес', 'Hardware Address']
    IP_SUBNET = ['IP / маска подсети', 'IP Address / Subnet Mask', 'IPv4 Address / Subnet Mask']
    GATEWAY = ['Шлюз', 'Gateway']


def find_all_values_by_label(html_soup, label_texts):
    """
    Находит ВСЕ ячейки с текстом из списка label_texts и возвращает список
    значений из соседних с ними ячеек. Для видеокарт, дисков, принтеров.
    Поддерживает мультиязычность.
    """
    if isinstance(label_texts, str):
        label_texts = [label_texts]

    values = []
    try:
        for label in label_texts:
            tags = html_soup.find_all('td', string=lambda text: text and label in text)
            for tag in tags:
                next_sibling = tag.find_next_sibling('td')
                if next_sibling:
                    values.append(next_sibling.get_text(strip=True))
    except Exception as e:
        print(f"Ошибка при поиске всех значений для '{label_texts}': {e}")
    return values


def _parse_network_info(html_soup):
    """
    Парсит сетевые адаптеры: MAC, IP/маска, шлюз.
    Поддерживает русский и английский языки.
    """
    adapters = []
    try:
        mac_labels = CInfo.MAC_ADDRESS
        ip_labels = CInfo.IP_SUBNET
        gateway_labels = CInfo.GATEWAY
        mac_address_tags = []
        for label in mac_labels:
            mac_address_tags.extend(
                html_soup.find_all('td', string=lambda text: text and label in text)
            )
        print(f"[DEBUG] Найдено MAC-адресов: {len(mac_address_tags)}")

        for mac_tag in mac_address_tags:
            table = mac_tag.find_parent('table')
            if not table:
                continue
            mac_address = mac_tag.find_next_sibling('td').get_text(strip=True)
            ip_tag = None
            for label in ip_labels:
                ip_tag = table.find('td', string=lambda text: text and label in text)
                if ip_tag:
                    break
            ip_subnet = ip_tag.find_next_sibling('td').get_text(strip=True) if ip_tag else "Не назначен"
            gateway_tag = None
            for label in gateway_labels:
                gateway_tag = table.find('td', string=lambda text: text and text.strip() == label)
                if gateway_tag:
                    break
            gateway = gateway_tag.find_next_sibling('td').get_text(strip=True) if gateway_tag else "Не найдено"

            adapter_info = {
                'mac': mac_address,
                'ip_subnet': ip_subnet,
                'gateway': gateway
            }
            adapters.append(adapter_info)
            print(f"[DEBUG] Добавлен адаптер: {adapter_info}")

    except Exception as e:
        print(f"Ошибка при парсинге сетевой информации: {e}")
    return adapters


def _parse_disk_space(html_soup):
    """
    Улучшенная функция для парсинга свободного места.
    Поддерживает оба языка: ищет "Свободно" или "Free".
    """
    # На данный момент не работает, будет исправлена в других версиях
    disk_spaces = []
    try:
        header = None
        for label in ['Свободно', 'Free']:
            header = html_soup.find('td', class_='th', string=re.compile(label))
            if header:
                break

        if not header:
            return []

        table = header.find_parent('table')
        headers = [h.get_text(strip=True) for h in table.find_all('td', class_='th')]

        free_label = None
        for label in ['Свободно', 'Free']:
            if label in headers:
                free_label = label
                break

        if not free_label:
            return []

        free_space_column_index = headers.index(free_label)

        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')
            if len(columns) > free_space_column_index:
                free_space_text = columns[free_space_column_index].get_text(strip=True)
                parts = free_space_text.split()
                if len(parts) == 2:
                    value, unit = parts
                    try:
                        value = float(value)
                        free_gb = 0
                        if unit.upper() in ['МБ', 'MB']:
                            free_gb = value / 1024
                        elif unit.upper() in ['ГБ', 'GB']:
                            free_gb = value
                        elif unit.upper() in ['ТБ', 'TB']:
                            free_gb = value * 1024

                        if free_gb > 0:
                            disk_spaces.append(f"{free_gb:.1f} ГБ")
                    except ValueError:
                        continue
    except Exception as e:
        print(f"Ошибка при парсинге места на дисках: {e}")
    return disk_spaces


def find_value_by_label(html_soup, label_texts):
    """
    Ищет ячейку с текстом из списка label_texts и возвращает значение из соседней ячейки.
    Поддерживает мультиязычность.
    """
    if isinstance(label_texts, str):
        label_texts = [label_texts]

    try:
        for label in label_texts:
            tag = html_soup.find('td', string=lambda text: text and label in text)
            if tag:
                return tag.find_next_sibling('td').get_text(strip=True)
    except AttributeError:
        return "Не найдено"
    return "Не найдено"


class ShortInfo(Screen):
    toggle_icon = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.music = SoundLoader.load(FILE_MUSIC)
        if self.music:
            self.music.loop = True
        else:
            print(f"Не удалось загрузить музыку: {FILE_MUSIC}")

    def _parse_ram_info(self, html_soup):
        """
        Находит все модули оперативной памяти.
        Поддерживает оба языка.
        """
        found_modules = []
        size_labels = CInfo.RSIZE if isinstance(CInfo.RSIZE, list) else [CInfo.RSIZE]

        size_tags = []
        for label in size_labels:
            size_tags.extend(
                html_soup.find_all('td', string=lambda text: text and label in text)
            )

        for size_tag in size_tags:
            try:
                module_table = size_tag.find_parent('table')
                if not module_table:
                    continue

                size = size_tag.find_next_sibling('td').get_text(strip=True)

                ram_type_tag = None
                for label in (CInfo.RTYPE if isinstance(CInfo.RTYPE, list) else [CInfo.RTYPE]):
                    ram_type_tag = module_table.find('td', string=lambda text: text and label in text)
                    if ram_type_tag:
                        break
                ram_type = ram_type_tag.find_next_sibling('td').get_text(strip=True) if ram_type_tag else ""

                speed_tag = None
                for label in (CInfo.RSPEED if isinstance(CInfo.RSPEED, list) else [CInfo.RSPEED]):
                    speed_tag = module_table.find('td', string=lambda text: text and label in text)
                    if speed_tag:
                        break
                speed = speed_tag.find_next_sibling('td').get_text(strip=True) if speed_tag else ""

                module_info = f"{size} {ram_type} ({speed})"
                found_modules.append(module_info)
            except AttributeError:
                continue

        return found_modules

    def toggle_music(self, obj):
        if not self.music:
            return

        if obj.icon == 'stop':
            self.music.play()
            self.toggle_icon.icon = 'play'
        else:
            self.music.stop()
            self.toggle_icon.icon = 'stop'

    def process_file(self, file_path: str):
        """Главный метод обработки файла."""
        decoded_path = unquote(file_path)
        if not decoded_path or not decoded_path.lower().endswith(EXT_FILE):
            self.send_error_msg(decoded_path if decoded_path else "")
            return
        try:
            with io.open(os.path.abspath(decoded_path), 'rb') as f:
                html = BeautifulSoup(f, PARSER)
            self.parse_and_display(html)

        except (FileNotFoundError, PermissionError, OSError):
            self.send_error_msg(decoded_path)

    def parse_and_display(self, html):
        """
        Главная функция парсинга. Сетевая информация выводится только в общем отчете.
        """
        report_title = html.title.text if html.title else "Отчет AIDA"
        all_disks = find_all_values_by_label(html, CInfo.DISK_DRIVE)
        all_printers = find_all_values_by_label(html, CInfo.PRINTER)

        data = {
            'Процессор': find_value_by_label(html, CInfo.CPTYPE),
            'Материнская плата': find_value_by_label(html, CInfo.MOTHERB),
            'ОС': find_value_by_label(html, CInfo.OS),
            'Видеокарты': find_all_values_by_label(html, CInfo.VIDEOA),
            'Диски': [disk for disk in all_disks if 'USB' not in disk and 'USB' not in disk.upper()],
            'Принтеры': [printer for printer in all_printers if printer not in ['Да', 'Нет', 'Yes', 'No']],
            'Место на дисках': _parse_disk_space(html),
            'Сетевые адаптеры': _parse_network_info(html),
        }

        ram_modules = self._parse_ram_info(html)
        data['Оперативная память'] = ", ".join(ram_modules) if ram_modules else find_value_by_label(html, CInfo.RAM_TOTAL)
        info_lines = [
            f"Процессор: {data['Процессор']}",
            f"Материнская плата: {data['Материнская плата']}",
            f"Оперативная память: {data['Оперативная память']}",
            f"ОС: {data['ОС']}",
        ]

        for i, disk in enumerate(data['Диски']):
            info_lines.append(f"Диск {i + 1}: {disk}")

        for i, adapter in enumerate(data['Сетевые адаптеры']):
            info_lines.append(f"--- Сетевой адаптер {i + 1} ---")
            info_lines.append(f"  MAC-адрес: {adapter['mac']}")
            info_lines.append(f"  IP / Маска: {adapter['ip_subnet']}")
            info_lines.append(f"  Шлюз: {adapter['gateway']}")

        for i, printer in enumerate(data['Принтеры']):
            info_lines.append(f"Принтер {i + 1}: {printer}")
        compact_parts = [
            data.get('Процессор', 'Не найдено'),
            data.get('Материнская плата', 'Не найдено'),
            ", ".join(data.get('Видеокарты', [])),
            data.get('Оперативная память', 'Не найдено'),
            ", ".join(data.get('Диски', [])),
            ", ".join(data.get('Место на дисках', [])),
            data.get('ОС', 'Не найдено'),
        ]
        compact_parts = [part for part in compact_parts if part]
        final_text = (
            f"{report_title}\n\n"
            f"--- Общая информация ---\n"
            f"{'\n'.join(info_lines)}\n\n"
            f"--- Строка для копирования ---\n"
            f"{'\\'.join(compact_parts)}"
        )

        self.manager.current = 'ResultScreen'
        self.manager.get_screen('ResultScreen').update_text_input(final_text)

    def send_error_msg(self, data: str):
        popup = CustomPopup()
        popup.update_content(data)
        popup.open()


class FileChooserScreen(Screen):
    def select_file(self, selection):
        if not selection:
            return

        selected_path = selection[0]
        short_info_screen = self.manager.get_screen('ShortInfo')
        short_info_screen.ids.data.text = selected_path
        self.manager.current = 'ShortInfo'
        short_info_screen.process_file(selected_path)


class ResultScreen(Screen):
    input_data = ObjectProperty()

    def update_text_input(self, data: str):
        self.input_data.text = data

    def get_back_and_clean(self):
        self.input_data.text = ''
        self.manager.current = 'ShortInfo'

    def copy_results(self):
        try:
            compact_string = self.input_data.text.split("--- Строка для копирования ---\n")[1]
            Clipboard.copy(compact_string)
        except IndexError:
            Clipboard.copy(self.input_data.text)


class CustomPopup(Popup):
    error_info = ObjectProperty()

    def update_content(self, data: str):
        message = ""
        if not data:
            message = ERR_EMPTY_LINE
        elif not data.lower().endswith(EXT_FILE):
            message = ERR_WRONG_EXT
        else:
            display_path = f"...{data[-30:]}" if len(data) > 30 else data
            message = f'\n{display_path}'
        self.error_info.text = ERR_MSG_TXT + message


class ShortInfoApp(MDApp):
    def build(self):
        self.title = TITLE
        self.icon = ICON_ASSET
        Window.size = (840, 440)
        Config.set('graphics', 'resizable', '0')
        Config.write()

        sm = ScreenManager()
        sm.add_widget(ShortInfo(name='ShortInfo'))
        sm.add_widget(ResultScreen(name='ResultScreen'))
        sm.add_widget(FileChooserScreen(name='FileChooserScreen'))
        return sm


if __name__ == '__main__':
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))

    ShortInfoApp().run()
