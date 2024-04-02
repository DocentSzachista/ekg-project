from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.properties import StringProperty
from kivy.graphics import Color, Rectangle
from ecg_screen import ECGPlot
from os.path import splitext

instructions = """ Jest to analizator plików EKG.
    Jak z niego korzystać?
    Należy wybrać za pomocą aplikacji plik z zapisanym sygnałem EKG który znajduje się 
    w wybranej lokalizacji na dysku. Musi on miec rozszerzenie '.hea'. 
    Następnie aplikacja pokaże wykres EKG na podstawie którego będzie można sprawdzić czy dana osoba ma arytmię.
    Program po kliknięciu przycisk będzie umiał powiedzieć jaką arytmię ma dana osoba.
"""



class FileLoaderScreen(Screen):
    """Screen który wczyta dane z pliku mat bądź hea"""
    def __init__(self, **kwargs):
        super(FileLoaderScreen, self).__init__(**kwargs)
        # self.layout = Button(text='Go to Screen Two', on_press=self.open_file_dialog)
        # self.add_widget(self.layout)

        with self.canvas.before:
            Color(0.8, 0.8, 0.8, 1)  # kolor tła (szary)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

        self.layout = Button(text='Open File Dialog', size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.6})
        self.layout.bind(on_press=self.open_file_dialog)
        self.add_widget(self.layout)

        self.app_info = Button(text='App Information', size_hint=(0.5, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        self.app_info.bind(on_press=self.show_info)
        self.add_widget(self.app_info)

    def _update_rect(self, instance, value):
        self.rect.pos = self.pos
        self.rect.size = self.size


    def switch_screen(self, instance):
        self.manager.current = 'ECG'

    def open_file_dialog(self, instance):
        file_chooser = FileChooserListView(path="/home")
        file_chooser.filters = ['*.hea', '*.mat', "*.dat"]  # Definiujemy filtry dla rozszerzeń
        file_chooser.bind(on_submit=self.selected)
        self.popup = Popup(title='Select File', content=file_chooser, size_hint=(None, None), size=(600, 400))
        self.popup.open()
    
    def selected(self, instance, selection, touch):
        if selection:
            path = splitext(selection[0])[0]
            self.manager.get_screen('ECG').plot.load_file(path)
            self.manager.current = 'ECG'
            self.popup.dismiss()

    def show_info(self, instance):
        info_popup = Popup(title='Informacje o aplikacji', content=Label(text=instructions), size_hint=(None, None), size=(600, 400))
        info_popup.open()

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
    MyApp().run()
