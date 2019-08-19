import datetime
import random
from typing import Iterable

from guacamole.c4.client import GameClient
from guacamole.c4.game import GameStateController, GameState


class GameSolver:

    def __init__(self, controller: GameStateController, players: Iterable[GameClient], stop_condition_fx):
        self._controller, self.players, self._stop_condition_fx = controller, list(players), stop_condition_fx
        self._won_counts = [0, 0]
        self._game_plays = 0
        self._last_print = datetime.datetime.now()

    def solve(self):
        while not self._stop_condition_fx():
            self.play_game()
            self._controller.reset()
            self.print_stats()

    def print_stats(self):
        if datetime.datetime.now() - self._last_print > datetime.timedelta(seconds=30):
            self._last_print = datetime.datetime.now()
            print(self._last_print)
            print('P1 win rate: {}'.format(self._won_counts[0] / self._game_plays))
            print('P2 win rate: {}'.format(self._won_counts[1] / self._game_plays))
            print('Tie rate: {}'.format(((self._game_plays - sum(self._won_counts)) / self._game_plays)))
            print('Total games: {}'.format(self._game_plays))
            print(flush=True)
            self.players[0].save()
            self.players[1].save()

    def play_game(self):
        player_idx = random.randint(0, 1)
        cur_player = self.players[player_idx]

        while self._controller.game_state() == GameState.ACTIVE:
            while not self._controller.drop_token(cur_player.provide_action(), cur_player.token):
                cur_player.bad_move()
            player_idx += 1
            player_idx %= 2
            cur_player = self.players[player_idx]
            # self._controller.print_board()

        if self._controller.game_state() == GameState.TIE:
            self.players[0].tie()
            self.players[1].tie()
        elif self._controller.game_state() == GameState.WINNER_PLAYER_1:
            self.players[0].won()
            self.players[1].lost()
            self._won_counts[0] += 1
        else:
            self.players[0].lost()
            self.players[1].won()
            self._won_counts[1] += 1
        self._game_plays += 1
