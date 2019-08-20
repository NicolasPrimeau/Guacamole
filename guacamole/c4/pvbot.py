from guacamole.c4.game import GameStateController, GameToken
from guacamole.c4.input_client import InputClient
from guacamole.c4.qclient import QClient
from guacamole.c4.solver import GameSolver


def main():
    controller = GameStateController()
    player1 = InputClient(controller, GameToken.PLAYER1)
    player2 = QClient(controller, GameToken.PLAYER2, save_path="states/player2.dat")
    player2.load()
    solver = GameSolver(controller, [player1, player2], lambda: False)
    solver.solve()


if __name__ == '__main__':
    main()
