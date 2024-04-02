from kivy.uix.boxlayout import BoxLayout
from kivy_garden.matplotlib import FigureCanvasKivyAgg
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.properties import StringProperty

import matplotlib.pyplot as plt
import wfdb


from kivy.uix.button import Button

class ECGPlot(BoxLayout):
    # chosen_file = StringProperty()

    def __init__(self, **kwargs):
        super(ECGPlot, self).__init__(**kwargs)
        # self.filename = "./HR00001"
        self.orientation="vertical"
        self.current_index = 0
        self.create_layout()

    def load_file(self, filepath: str):
        self.record = wfdb.rdrecord(filepath)
        self.sampling_rate = 500
        self.data = self.record.p_signal.T
        self.update_plot()


    def create_buttons_layout(self):
        self.button_layout = BoxLayout(orientation='vertical', size_hint=(0.2, 1))
        switch_button = Button(text='Switch', size_hint=(1, 1))
        next_button = Button(text='Next', size_hint=(1, 1))
        prev_button = Button(text='Previous', size_hint=(1, 1))
        next_button.bind(on_press= self.load_next)
        prev_button.bind(on_press= self.load_previous)

        # Dodawanie przycisków do układu
        self.button_layout.add_widget(switch_button)
        self.button_layout.add_widget(next_button)
        self.button_layout.add_widget(prev_button)

    def create_plot_button_layout(self):
        self.create_buttons_layout()

        self.main_layout = BoxLayout(orientation="horizontal", size_hint=(1, 0.8))
        self.fig, self.axis = plt.subplots(1, 1)
        self.myplottings = FigureCanvasKivyAgg(figure=self.fig)

        self.main_layout.add_widget(self.myplottings)
        self.main_layout.add_widget(self.button_layout)



    def create_layout(self):
        self.create_plot_button_layout()
        

        self.extra_data_input = TextInput(multiline=True, size_hint=(1, 0.2))
        self.extra_data_input.text="A wiedzą państwo że płacili mi za kopanie kobiet prądem? :D"
        self.extra_data_input.disabled = True

        # Dodawanie Carousel i przycisków do interfejsu
        self.add_widget(self.extra_data_input)
        self.add_widget(self.main_layout)
        # self.update_plot()

    def load_next(self, instance):
        self.current_index = (self.current_index + 1) % self.data.shape[0]
        self.update_plot()

    def load_previous(self, instance):
        self.current_index = (self.current_index - 1) % self.data.shape[0]
        self.update_plot()

    def update_plot(self):
        # Pobranie aktualnego subplotu
        self.axis.cla()
        chosen_plot = self.data[self.current_index]
        self.axis.plot(chosen_plot[::self.sampling_rate])
        self.axis.set_ylabel("Woltarz")
        self.axis.set_xlabel("Czas [s]")
        self.fig.canvas.draw()


class MyApp(App):
    def build(self):
        return ECGPlot()

if __name__ == "__main__":
    MyApp().run()


# print(description.keys())