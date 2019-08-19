import unittest

from guacamole.c4.game import GameStateController, GameToken, GameState


class GameStateControllerTest(unittest.TestCase):

    def test_win_cols(self):
        controller = GameStateController()
        controller.drop_token(0, GameToken.PLAYER1)
        controller.drop_token(0, GameToken.PLAYER1)
        controller.drop_token(0, GameToken.PLAYER1)
        controller.drop_token(0, GameToken.PLAYER1)
        self.assertEqual(GameState.WINNER_PLAYER_1, controller.game_state())

    def test_win_rows(self):
        controller = GameStateController()
        controller.drop_token(0, GameToken.PLAYER1)
        controller.drop_token(1, GameToken.PLAYER1)
        controller.drop_token(2, GameToken.PLAYER1)
        controller.drop_token(3, GameToken.PLAYER1)
        self.assertEqual(GameState.WINNER_PLAYER_1, controller.game_state())

    def test_win_diag(self):
        controller = GameStateController()
        controller.drop_token(0, GameToken.PLAYER1)
        controller.drop_token(1, GameToken.PLAYER2)
        controller.drop_token(1, GameToken.PLAYER1)
        controller.drop_token(2, GameToken.PLAYER2)
        controller.drop_token(2, GameToken.PLAYER2)
        controller.drop_token(2, GameToken.PLAYER1)
        controller.drop_token(3, GameToken.PLAYER2)
        controller.drop_token(3, GameToken.PLAYER2)
        controller.drop_token(3, GameToken.PLAYER2)
        controller.drop_token(3, GameToken.PLAYER1)
        self.assertEqual(GameState.WINNER_PLAYER_1, controller.game_state())

    def test_win_diag_2(self):
        controller = GameStateController()
        controller.drop_token(3, GameToken.PLAYER1)
        controller.drop_token(2, GameToken.PLAYER2)
        controller.drop_token(2, GameToken.PLAYER1)
        controller.drop_token(1, GameToken.PLAYER2)
        controller.drop_token(1, GameToken.PLAYER2)
        controller.drop_token(1, GameToken.PLAYER1)
        controller.drop_token(0, GameToken.PLAYER2)
        controller.drop_token(0, GameToken.PLAYER2)
        controller.drop_token(0, GameToken.PLAYER2)
        controller.drop_token(0, GameToken.PLAYER1)
        self.assertEqual(GameState.WINNER_PLAYER_1, controller.game_state())

    def test_tie(self):
        controller = GameStateController()
        token1, token2 = GameToken.PLAYER1, GameToken.PLAYER2
        for j in range(0, controller.size()):
            for i in range(0, controller.size()):
                if 0 <= i <= 1 or 4 <= i <= 5:
                    controller.drop_token(j, token1)
                else:
                    controller.drop_token(j, token2)
            token1, token2 = token2, token1
        self.assertEqual(GameState.TIE, controller.game_state())
