from guacamole.c4.game import GameStateController, GameToken
from guacamole.c4.qclient import QClient
from guacamole.c4.solver import GameSolver


def main():
    controller = GameStateController()
    player1 = QClient(controller, GameToken.PLAYER1, save_path="states/player1.dat")
    print('Loading player 1')
    if not player1.load():
        print('Failed to load player 1!')
    player2 = QClient(controller, GameToken.PLAYER2, save_path="states/player2.dat")
    print('Loading player 2')
    if not player2.load():
        print('Failed to load player 2!')
    solver = GameSolver(controller, [player1, player2], lambda: False)
    solver.solve()


if __name__ == '__main__':
    main()
