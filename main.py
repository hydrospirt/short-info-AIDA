import os
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config

__version__ = '0.1'

Config.set('kivy', 'resizable', False)


class ShortInfo(GridLayout):
    file_path = ...


class ShortInfoApp(App):
    def build(self):
        return ShortInfo()


if __name__ == '__main__':
    ShortInfoApp().run()
