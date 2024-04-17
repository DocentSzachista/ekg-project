from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label


class CustomButton(Button):
    custom = None

    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)




class WidgetContainer(GridLayout):
    """Slider do przesuwania wartości."""   
    def __init__(self, value_name :str, description: str, minimum = 0, maximum=10, value = 1, **kwargs):
        super(WidgetContainer, self).__init__(**kwargs) 
        self.value = value
        self.description = description
        self.cols = 3         
        self.slider = Slider(min = minimum, max = maximum, value=self.value) 
        self.add_widget(Label(text = value_name))
        self.add_widget(self.slider) 
        self.brightnessValue = Label(text =f'{self.description}: {value}s')
        self.add_widget(self.brightnessValue)
        self.slider.bind(value = self.on_value)
        
    # Adding functionality behind the slider
    # i.e when pressed increase the value
    def on_value(self, instance, value):
        self.value = int(value)
        self.brightnessValue.text = f"{self.description}: {int(value)}s"