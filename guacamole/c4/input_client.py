from abc import ABC

from guacamole.c4.game import GameStateController
from guacamole.xo.game import GameToken


class InputClient(ABC):

    def __init__(self, controller: GameStateController, token: GameToken):
        self.controller, self.token = controller, token
        self.stop = False

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
                x = int(input('Provide col: ')) - 1
                print()
                if 0 <= x < self.controller.size():
                    return x
            except ValueError as e:
                pass
            print('Bad input')

    def bad_move(self):
        pass

    def lost(self):
        self._end_game('You lost!')

    def won(self):
        self._end_game('You won!')

    def tie(self):
        self._end_game('Tie!')

    def _end_game(self, msg):
        print('=' * len('|   |   |   |   |   |   |   |   |'))
        print()
        self.controller.print_board(help=False)
        print()
        print(msg)
        print()
        print()
        print('=' * len('|   |   |   |   |   |   |   |   |'))
        print()
        x = str(input('Play again? ')).lower()
        self.stop = x != 'y'
