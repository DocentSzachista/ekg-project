from kivy.logger import LOG_LEVELS, Logger
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from ecg_screen import ECGPlot
from file_loader import FileLoaderScreen
from os import makedirs

class ECGScreen(Screen):

    """Screen który wydrukuje EKG i ma możliwość przepytania modelu czy jest dana arytmia wykryta"""
    def __init__(self, **kwargs):
        super(ECGScreen, self).__init__(**kwargs)
        self.plot = ECGPlot()
        self.add_widget(self.plot)

    def switch_screen(self, instance):
        self.manager.current = 'file'


class MyApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "ECG analyzer"

    def build(self):
        sm = ScreenManager()
        sm.add_widget(FileLoaderScreen(name='file'))
        sm.add_widget(ECGScreen(name='ECG'))
        return sm

if __name__ == '__main__':
    Logger.setLevel(LOG_LEVELS["debug"])
    makedirs("./ekg_path", exist_ok=True)
    MyApp().run()
