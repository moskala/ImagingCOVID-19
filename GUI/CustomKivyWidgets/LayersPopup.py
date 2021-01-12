# Kivy imports
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

# Python imports
import sys
import os

# Implemented methods imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Methods')))
from ChooseSlices import LayerChoice, LayerChoiceType


class LayersPopup(Popup):

    def __init__(self, layer_choice: LayerChoice, max_layers_range=1):
        super().__init__()

        self.max_layers_range = max_layers_range

        grid = GridLayout(cols=3,
                          row_force_default=True,
                          row_default_height=30,
                          spacing=(10, 10))

        self.box_range = CheckBox(width=50, size_hint=(None, 1))
        self.box_collection = CheckBox(width=50, size_hint=(None, 1))
        self.box_single = CheckBox(width=50, size_hint=(None, 1))

        self.box_range.group = "choice"
        self.box_collection.group = "choice"
        self.box_single.group = "choice"

        label_range = Label(text="Layers range", width=100, size_hint=(None, 1))
        label_collection = Label(text="User's choice", width=100, size_hint=(None, 1))
        label_single = Label(text="Single layer", width=100, size_hint=(None, 1))

        label_range.bind(size=label_range.setter('text_size'))
        label_collection.bind(size=label_collection.setter('text_size'))
        label_single.bind(size=label_single.setter('text_size'))

        # First row
        grid.add_widget(self.box_single)
        grid.add_widget(label_single)
        text_single = "Current layer: "+str(layer_choice.single_layer+1)
        single_info = Label(text=text_single)
        single_info.bind(size=single_info.setter('text_size'))
        grid.add_widget(single_info)

        # Second row
        grid.add_widget(self.box_collection)
        grid.add_widget(label_collection)
        collection_text = "Number of chosen layers: {0}".format(len(layer_choice.collection_layers))
        collection_info = Label(text=collection_text)
        collection_info.bind(size=collection_info.setter('text_size'))
        grid.add_widget(collection_info)

        # Third row
        grid.add_widget(self.box_range)
        grid.add_widget(label_range)
        range_info = Label(text="Enter range: ", halign='justify', size_hint=(None, 1))
        range_info.bind(size=range_info.setter('text_size'))

        input_box = BoxLayout(orientation='horizontal', spacing=10, padding=(0, 0, 10, 0))
        input_box.add_widget(range_info)

        label_from = Label(text="From: ", halign='right')
        label_from.bind(size=label_from.setter('text_size'))
        input_box.add_widget(label_from)

        self.input_from = TextInput(multiline=False, input_type='number', input_filter='int')
        input_box.add_widget(self.input_from)

        label_to = Label(text="To: ", halign='right')
        label_to.bind(size=label_to.setter('text_size'))
        input_box.add_widget(label_to)

        self.input_to = TextInput(multiline=False, input_type='number', input_filter='int')
        input_box.add_widget(self.input_to)

        grid.add_widget(input_box)

        if layer_choice.choice_type == LayerChoiceType.SINGLE:
            self.box_single.active = True
        elif layer_choice.choice_type == LayerChoiceType.RANGE:
            val_from, val_to = layer_choice.get_choice_range()
            self.box_range.active = True
            self.input_to.text = str(val_to + 1)
            self.input_from.text = str(val_from + 1)
        else:
            self.box_collection.active = True

        self.content.add_widget(grid, index=1)

        self.previous_choice = layer_choice

        # Warnign
        self.warning = Label(text='[color=ff0000]'
                                  'Wrong range values!\nShould be in range [1, {}].'                 
                                  '[/color]'.format(self.max_layers_range),
                             markup=True)

    def validate_range(self):
        try:
            val_from = int(self.input_from.text)-1
            val_to = int(self.input_to.text)-1
            if val_from <= val_to  and val_from >= 0 and val_to <= self.max_layers_range:
                return [val_from, val_to]
            else:
                return None
        except Exception as error:
            print(error)
            return None

    def get_settings(self):
        if self.box_single.active:
            self.previous_choice.set_choice_type(LayerChoiceType.SINGLE)
            return self.previous_choice
        elif self.box_range.active:
            limits = self.validate_range()
            if limits is None:
                self.content.add_widget(self.warning, index=1)
                return None
            else:
                self.previous_choice.set_choice_range(limits[0], limits[1])
                return self.previous_choice
        elif self.box_collection.active:
            self.previous_choice.set_choice_type(LayerChoiceType.COLLECTION)
            return self.previous_choice
