import itertools
import json
import random
import uuid
from enum import Enum

import numpy as np


class GameToken(Enum):
    NOTHING = 0
    X_TOKEN = 1
    O_TOKEN = 2

    @staticmethod
    def from_val(val):
        for token in GameToken:
            if token.value == val:
                return token
        return None

    def __str__(self):
        return {
            GameToken.X_TOKEN: 'x',
            GameToken.O_TOKEN: 'o',
            GameToken.NOTHING: '.'
        }[self]


class GameState:

    def __init__(self, board_x=3, board_y=3):
        self._board = np.zeros((board_x, board_y))

    def set(self, x, y, token: GameToken) -> bool:
        if x >= self.x or y >= self.y:
            return False
        if self._board[x, y] != 0:
            return False
        self._board[x, y] = token.value
        return True

    @property
    def x(self):
        return self._board.shape[0]

    @property
    def y(self):
        return self._board.shape[1]

    def get(self, x, y) -> GameToken:
        return GameToken.from_val(self._board[x, y])

    def check_win(self):
        for i in range(self.x):
            if self.check_row(i):
                return True

        for i in range(self.y):
            if self.check_col(i):
                return True

        if self.check_diag() or self.check_diag(reverse=True):
            return True
        return False

    def check_row(self, row_idx: int) -> bool:
        return self._check_idxs([row_idx], list(range(self.y)))

    def check_col(self, col_idx: int) -> bool:
        return self._check_idxs(list(range(self.x)), [col_idx])

    def check_diag(self, reverse=False):
        xs = range(0, self.x)
        ys = range(0, self.y)
        if reverse:
            xs = reversed(xs)
        first = None
        for x, y in zip(xs, ys):
            if first is None:
                first = self._board[x][y]
            elif first == 0:
                return False
            elif self._board[x][y] != first:
                return False
        return True

    def _check_idxs(self, xs, ys) -> bool:
        first = None
        for x, y in itertools.product(xs, ys):
            if first is None:
                first = self._board[x][y]
            elif first == 0:
                return False
            elif self._board[x][y] != first:
                return False
        return True

    def check_tie(self):
        return len(list(filter(
            lambda x_y: self._board[x_y[0], x_y[1]] == 0,
            itertools.product(list(range(self.x)), list(range(self.y)))
        ))) == 0

    def encode(self):
        return json.dumps({'board': self._board.tolist()})

    @staticmethod
    def decode(data):
        board = json.loads(data).get('board', None)
        if not board:
            return None
        board = np.array(board)
        state = GameState(board_x=board.shape[0], board_y=board.shape[1])
        state._board = board
        return state


class GameAction(Enum):
    WON = 1
    NEXT = 2
    TIE = 3
    LOSS = 4
    INVALID = 5

    @staticmethod
    def from_code(val):
        for action in GameAction:
            if action.value == val:
                return action
        return GameAction.INVALID


class GameController:

    def __init__(self, board_dims=(3, 3)):
        self._dims = board_dims
        self.state = GameState(board_x=self._dims[0], board_y=self._dims[1])
        self.players = [str(uuid.uuid4()), str(uuid.uuid4())]
        self._current_player_idx = random.randint(0, len(self.players) - 1)
        self._tokens = {
            self.players[0]: GameToken.X_TOKEN,
            self.players[1]: GameToken.O_TOKEN
        }
        self.winner = None
        self.is_tie = False

    def token(self, player_id):
        return self._tokens[player_id]

    @property
    def current_player(self):
        return self.players[self._current_player_idx]

    def do_move(self, player_id, x, y) -> GameAction:
        if player_id not in self.players or self.players.index(player_id) != self._current_player_idx:
            return GameAction.INVALID

        if self.is_tie:
            return GameAction.TIE

        if self.winner and self.winner == player_id:
            return GameAction.WON

        if self.winner and self.winner != player_id:
            return GameAction.LOSS

        if not self.state.set(x, y, self._tokens[player_id]):
            return GameAction.INVALID

        if self.state.check_win():
            self.winner = player_id
            return GameAction.WON

        if self.state.check_tie():
            self.is_tie = True
            return GameAction.TIE
        self._current_player_idx += 1
        self._current_player_idx %= len(self.players)
        return GameAction.NEXT
