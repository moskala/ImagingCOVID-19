# Python imports
from enum import Enum


class LayerChoiceType(Enum):
    SINGLE = 0,
    RANGE = 1,
    COLLECTION = 2


class LayerChoice:

    def __init__(self):
        self.choice_type = LayerChoiceType.SINGLE
        self.single_layer = 0
        self.collection_layers = []
        self.start_layer = 0
        self.end_layer = 0

    def get_choice_type(self):
        return self.choice_type

    def set_choice_type(self, chosen_type):
        self.choice_type = chosen_type

    def set_choice_singular(self, layer_number):
        self.choice_type = LayerChoiceType.SINGLE
        self.single_layer = layer_number

    def update_choice_singular(self, layer_number):
        self.single_layer = layer_number

    def set_choice_range(self, start_layer, end_layer):
        self.choice_type = LayerChoiceType.RANGE
        self.start_layer = start_layer
        self.end_layer = end_layer

    def set_choice_collection(self, layers):
        self.choice_type = LayerChoiceType.COLLECTION
        self.collection_layers = layers

    def choose_indexes(self):
        if self.choice_type == LayerChoiceType.COLLECTION:
            return self.collection_layers
        elif self.choice_type == LayerChoiceType.RANGE:
            return list(range(self.start_layer, self.end_layer+1, 1))
        else:
            return [self.single_layer]

    def append_collection_layer(self, layer):
        self.collection_layers.append(layer)

    def remove_collection_layer(self, layer):
        self.collection_layers.remove(layer)

    def check_collection_layer(self, layer):
        return layer in self.collection_layers

    def check_range(self):
        if self.choice_type == LayerChoiceType.RANGE:
            return self.start_layer <= self.end_layer
        else:
            return True
