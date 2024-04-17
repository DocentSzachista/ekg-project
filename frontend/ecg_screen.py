import matplotlib.pyplot as plt
import wfdb
import seaborn as sns
from kivy.logger import Logger
from kivy_garden.matplotlib import FigureCanvasKivyAgg

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from utils import CustomButton
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown


instructions = """ 
Jest to analizator plików EKG.
Jak z niego korzystać?
Należy wybrać za pomocą aplikacji plik z zapisanym sygnałem EKG, 
który znajduje się w wybranej lokalizacji na dysku. 
Musi on miec rozszerzenie '.hea', `.mat` bądź `.dat`. 
Następnie aplikacja pokaże wykres EKG, na podstawie 
którego będzie można sprawdzić czy dana osoba ma arytmię.
Program po kliknięciu przycisk będzie umiał powiedzieć 
jaką arytmię ma dana osoba.
"""



class ECGPlot(BoxLayout):
    
    def __init__(self, **kwargs):
        self.plot_x_max = 1
        self.plot_x_min = 0
        self.sampling_rate = 500

        super(ECGPlot, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.current_index = 0
        self.create_layout()
        sns.set_style("whitegrid")

# Sekcja z layout'em ------------------------------------------------------------------

    def create_buttons_layout(self):
        """Tworzenie przycisków w odpowiednim układzie."""
        self.button_layout = BoxLayout(
            orientation='horizontal', size_hint=(1, 0.1))

        # Przyciski
        next_button = Button(text='Przesuń do przodu', size_hint=(1, 1))
        prev_button = Button(text='Przesuń do tyłu', size_hint=(1, 1))

        # Bindowanie do funkcji
        next_button.bind(on_press=self.move_right)
        prev_button.bind(on_press=self.move_left)

        # Dodawanie przycisków do układu
        
        self.button_layout.add_widget(prev_button)
        self.button_layout.add_widget(next_button)


    def create_navbar(self):
        self.navbar_layout = BoxLayout(
            orientation='horizontal', size_hint=(1, 0.05))
        diagnosis_button = Button(text='Zrób analizę', size_hint=(0.4, 1))

        titles = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

        
        dropdown_plot = DropDown()
        for option, index in zip(titles, range(len(titles))):
            btn = CustomButton(text=option, size_hint_y=None, height=40)
            btn.custom = index
            btn.bind(on_release=lambda btn: dropdown_plot.select([btn.text, btn.custom]))
            dropdown_plot.add_widget(btn)
        
        # Dodaj przycisk do wywołania rozwijalnego menu
        self.menu_button = Button(text='Kanał: I', size_hint=(0.5, 1),) #size=(100, 50))  # Ustawiamy rozmiar przycisku
        self.menu_button.bind(on_release=dropdown_plot.open)
        dropdown_plot.bind(on_select=lambda instance, x: self.update_selection(x[0], x[1]))
        
        dropdown_options = DropDown()
        help_button = Button(text="Pomoc", size_hint=(0.3, 1))
        help_button.bind(on_release=dropdown_options.open)
        options_button = Button(text="Ustawienia", size_hint_y=None, height=40)
        instruction_button = Button(text="Informacje", size_hint_y=None, height=40)

        instruction_button.bind(on_press=self.show_info)

        dropdown_options.add_widget(options_button)
        dropdown_options.add_widget(instruction_button)



        # self.dropdown_button.bind(on_select=self.update_selection)
        diagnosis_button.bind(on_press=self.make_diagnosis)

        self.navbar_layout.add_widget(diagnosis_button)
        self.navbar_layout.add_widget(self.menu_button)
        self.navbar_layout.add_widget(help_button)


    def create_layout(self):
        # self.create_plot_button_layout()
        self.create_navbar()
        self.create_buttons_layout()
        self.fig, self.axis = plt.subplots(1, 1)
        self.myplottings = FigureCanvasKivyAgg(figure=self.fig)

        # Dodawanie Carousel i przycisków do interfejsu
        self.add_widget(self.navbar_layout)
        self.add_widget(self.myplottings)
        self.add_widget(self.button_layout)
        # self.update_plot()


# Sekcja z funkcjami do guzików itp --------------------

    def show_info(self, instance):
        info_popup = Popup(title='Informacje o aplikacji', content=Label(text_size=(400, None),
                                                                         text=instructions), size_hint=(None, None), size=(600, 400))
        info_popup.open()



    def load_file(self, filepath: str):
        """
            Funkcja wczytująca plik matlabowy i wyciągająca informacje:
            - częstotliwość próbkowania sygnału
            - Sygnały EKG dla 12 różnych elektrod.
            - Nazwy sygnałów.
        """
        record = wfdb.rdrecord(filepath)
        self.sampling_rate = record.fs
        self.data = record.p_signal
        self.plot_titles = record.sig_name
        self.update_plot()

    def update_selection(self, text: str, index: int):
        """Aktualizuj selekcje jak i wybraną opcję w dropdownie."""
        self.current_index = index
        self.menu_button.text =f"Kanał: {text}"
        Logger.debug(self.current_index)
        self.update_plot()


    def move_left(self, instance):
        current_xlim = self.axis.get_xlim()
        current_start = int(current_xlim[0])
        new_start = max(0, current_start - self.sampling_rate)  # Przesunięcie o 10 jednostek w lewo
        new_end = new_start + (current_xlim[1] - current_xlim[0])
        self.axis.set_xlim(new_start, new_end)
        self.fig.canvas.draw()

    def move_right(self, instance):
        current_xlim = self.axis.get_xlim()
        current_end = int(current_xlim[1])
        new_end = min(len(self.data[:, self.current_index]), current_end + self.sampling_rate)  # Przesunięcie o 10 jednostek w prawo
        new_start = new_end - (current_xlim[1] - current_xlim[0])
        self.axis.set_xlim(new_start, new_end)
        self.fig.canvas.draw()

    def update_plot(self):
        """Aktualizacja wyświetlanego wykresu."""
        # Pobranie aktualnego subplotu
        self.axis.cla()
        chosen_plot = self.data[:,self.current_index]
        self.axis.plot(chosen_plot)
        self.axis.set_ylabel("Woltaż [mV]")
        self.axis.set_xlabel("Czas [s]")
        self.axis.set_title(self.plot_titles[self.current_index])
        ticks = [t  for t in range(len(chosen_plot[::self.sampling_rate])+1)]
        Logger.debug(f"FS: {self.sampling_rate} plots {ticks}")
        # Logger.debug(f"Debug: {[t for t in range()]}")
        ilosc_sekund = 10
        
        ticks = (range(0, int(5000) + 1, 500), [str(t) + 's' for t in range(0, int(ilosc_sekund) + 1)])
        self.axis.set_xticks(ticks[0])
        self.axis.set_xticklabels(ticks[1])
        self.axis.set_xlim(self.plot_x_min*self.sampling_rate, self.plot_x_max* self.sampling_rate)
        self.fig.canvas.draw()

    def make_diagnosis(self, instance):
        popup = DiagnosisPopUp()
        popup.open()





class DiagnosisPopUp(Popup):
    """Popup który wywołuje zawołania do modelu i zwraca informacje o diagnozie dla pacjenta."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_max = (350, 200)
        self.title = "Analiza"
        self.content = BoxLayout(
            orientation='vertical'
        )
        self.placeholder = "Stwierdzono następującą arytmię na podstawie wykresów: {}"
        self.label = Label(text=self.placeholder, text_size=(300, None), height=50,
                           halign='center',
                           valign='middle')
        exit_button = Button(text='Zamknij diagnoze', size_hint=(
            0.8, 0.4), pos_hint={'center_x': 0.5, 'center_y': 0.5})

        exit_button.bind(on_press=self.dismiss)

        self.content.add_widget(self.label)
        self.content.add_widget(exit_button)

    def on_open(self):
        """Wydarzenie co się stanie kiedy zostanie otwarty popup."""
        # TODO: Dodanie tutaj wywołania modelu dla danych.
        self.label.text = self.placeholder.format("Bradykardia")
        return super().on_open()
