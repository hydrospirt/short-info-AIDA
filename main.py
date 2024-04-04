import os
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.label import Label

__version__ = '0.1'


class ShortInfo(GridLayout):
    def __init__(self, **var_args):
        super(ShortInfo, self).__init__(**var_args)
        Window.size = (640, 340)
        Config.set('graphics', 'resizable', False)


class ShortInfoApp(App):
    def build(self):
        self.title = f'Short Info AIDA {__version__}'
        self.icon = 'icon/icon.png'
        return ShortInfo()


if __name__ == '__main__':
    ShortInfoApp().run()
