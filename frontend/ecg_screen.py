import matplotlib.pyplot as plt
import wfdb
import seaborn as sns

from kivy_garden.matplotlib import FigureCanvasKivyAgg

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label


class ECGPlot(BoxLayout):
    
    def __init__(self, **kwargs):
        super(ECGPlot, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.current_index = 0
        self.create_layout()
        sns.set_style("whitegrid")

# Sekcja z layout'em ------------------------------------------------------------------

    def create_buttons_layout(self):
        """Tworzenie przycisków w odpowiednim układzie."""
        self.button_layout = BoxLayout(
            orientation='vertical', size_hint=(0.2, 1))

        # Przyciski
        diagnosis_button = Button(text='Podaj diagnozę', size_hint=(1, 1))
        next_button = Button(text='Następny', size_hint=(1, 1))
        prev_button = Button(text='Poprzedni', size_hint=(1, 1))

        # Bindowanie do funkcji
        next_button.bind(on_press=self.load_next)
        prev_button.bind(on_press=self.load_previous)
        diagnosis_button.bind(on_press=self.make_diagnosis)

        # Dodawanie przycisków do układu
        self.button_layout.add_widget(diagnosis_button)
        self.button_layout.add_widget(next_button)
        self.button_layout.add_widget(prev_button)

    def create_plot_button_layout(self):
        """Połączenie układu przycisków z wykresem."""
        self.create_buttons_layout()

        self.main_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, 0.8))
        self.fig, self.axis = plt.subplots(1, 1)
        self.myplottings = FigureCanvasKivyAgg(figure=self.fig)

        self.main_layout.add_widget(self.myplottings)
        self.main_layout.add_widget(self.button_layout)

    def create_layout(self):
        self.create_plot_button_layout()

        self.extra_data_input = TextInput(multiline=True, size_hint=(1, 0.2))
        self.extra_data_input.text = "I am just a placeholder to take space."
        self.extra_data_input.disabled = True

        # Dodawanie Carousel i przycisków do interfejsu
        self.add_widget(self.extra_data_input)
        self.add_widget(self.main_layout)
        # self.update_plot()


# Sekcja z funkcjami do guzików itp --------------------

    def load_file(self, filepath: str):
        """
            Funkcja wczytująca plik matlabowy i wyciągająca informacje:
            - częstotliwość próbkowania sygnału
            - Sygnały EKG dla 12 różnych elektrod.
            - Nazwy sygnałów.
        """
        record = wfdb.rdrecord(filepath)
        self.sampling_rate = record.fs
        self.data = record.p_signal.T
        self.plot_titles = record.sig_name
        self.update_plot()

    def load_next(self, instance):
        """Event wywołujący wczytanie kolejnych danych w tablicy."""
        self.current_index = (self.current_index + 1) % self.data.shape[0]
        self.update_plot()

    def load_previous(self, instance):
        """Event wywołujący wczytanie poprzednich danych w tablicy."""
        self.current_index = (self.current_index - 1) % self.data.shape[0]
        self.update_plot()

    def update_plot(self):
        """Aktualizacja wyświetlanego wykresu."""
        # Pobranie aktualnego subplotu
        self.axis.cla()
        chosen_plot = self.data[self.current_index]
        self.axis.plot(chosen_plot[::self.sampling_rate])
        self.axis.set_ylabel("Woltaż")
        self.axis.set_xlabel("Czas [s]")
        self.axis.set_title(self.plot_titles[self.current_index])
        self.fig.canvas.draw()

    def make_diagnosis(self, instance):
        popup = DiagnosisPopUp()
        popup.open()


class DiagnosisPopUp(Popup):
    """Popup który wywołuje zawołania do modelu i zwraca informacje o diagnozie dla pacjenta."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_max = (350, 200)
        self.title = "Diagnoza"
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
