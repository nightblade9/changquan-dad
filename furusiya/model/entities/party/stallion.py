import colors
from model.components.ai.stallion import StallionAi
from model.entities.game_object import GameObject


class Stallion(GameObject):
    def __init__(self, player):
        super().__init__(0, 0, '=', 'stallion', color=colors.sepia, blocks=True)

        self.set_component(StallionAi(self))
        self.player = player