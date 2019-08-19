from abc import abstractmethod, ABC

from guacamole.c4.game import GameStateController
from guacamole.xo.game import GameToken


class GameClient(ABC):

    def __init__(self, controller: GameStateController, token: GameToken):
        self.controller, self.token = controller, token

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def provide_action(self) -> int:
        pass

    @abstractmethod
    def bad_move(self):
        pass

    @abstractmethod
    def lost(self):
        pass

    @abstractmethod
    def won(self):
        pass

    @abstractmethod
    def tie(self):
        pass
