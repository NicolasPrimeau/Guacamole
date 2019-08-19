from abc import ABC

from guacamole.c4.game import GameStateController
from guacamole.xo.game import GameToken


class InputClient(ABC):

    def __init__(self, controller: GameStateController, token: GameToken):
        self.controller, self.token = controller, token

    def save(self):
        pass

    def load(self):
        pass

    def provide_action(self) -> int:
        return self.get_input()

    def get_input(self):
        while True:
            self.controller.print_board()
            try:
                x = int(input('Provide col: '))
                print()
                if 0 <= x <= self.controller.size():
                    return x
            except ValueError as e:
                pass
            print('Bad input')

    def bad_move(self):
        pass

    def lost(self):
        print()
        print('You lost.')
        print()

    def won(self):
        print()
        print('You won.')
        print()

    def tie(self):
        print()
        print('Tie!')
        print()
