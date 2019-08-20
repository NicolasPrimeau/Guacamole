import itertools
from enum import Enum

import numpy as np


class GameToken(Enum):
    PLAYER1 = 1
    PLAYER2 = 2
    EMPTY = 0

    @staticmethod
    def from_val(val):
        for item in GameToken:
            if item.value == val:
                return item
        return None


class GameState(Enum):
    ACTIVE = 0
    WINNER_PLAYER_1 = 1
    WINNER_PLAYER_2 = 2
    TIE = 3


class GameStateController:

    def __init__(self, size=8, sequence=4):
        self._size, self.sequence = size, sequence
        self._state = GameState.ACTIVE
        self._board = np.zeros(shape=(self._size, self._size), dtype=np.int8)

    def reset(self):
        self._state = GameState.ACTIVE
        self._board = np.zeros(shape=(self._size, self._size), dtype=np.int8)

    def size(self) -> int:
        return self._size

    def encode(self):
        return tuple(tuple(x) for x in self._board[:])

    def drop_token(self, col, token: GameToken):
        for idx, i in enumerate(self._board[col]):
            if i == GameToken.EMPTY.value:
                self._board[col, idx] = token.value
                return True
        return False

    def print_board(self):
        for col in range(self.size()):
            print('{} : '.format(col), end='')
            for row in range(self.size()):
                print(self._board[col, row], end='')
                print(' ', end='')
            print()
        print()

    def game_state(self) -> GameState:
        if self._state != GameState.ACTIVE:
            return self._state

        for col in range(self._board.shape[0]):
            token = self._check_col(col)
            if token == GameToken.PLAYER1:
                self._state = GameState.WINNER_PLAYER_1
            elif token == GameToken.PLAYER2:
                self._state = GameState.WINNER_PLAYER_2

        for row in range(self._board.shape[1]):
            token = self._check_row(row)
            if token == GameToken.PLAYER1:
                self._state = GameState.WINNER_PLAYER_1
            elif token == GameToken.PLAYER2:
                self._state = GameState.WINNER_PLAYER_2

        for row, col in itertools.product(list(range(self._board.shape[0])), list(range(self._board.shape[1]))):
            token = self._check_diag_up(row, col)
            if token == GameToken.PLAYER1:
                self._state = GameState.WINNER_PLAYER_1
            elif token == GameToken.PLAYER2:
                self._state = GameState.WINNER_PLAYER_2

        for row, col in itertools.product(list(range(self._board.shape[0])), list(range(self._board.shape[1]))):
            token = self._check_diag_down(row, col)
            if token == GameToken.PLAYER1:
                self._state = GameState.WINNER_PLAYER_1
            elif token == GameToken.PLAYER2:
                self._state = GameState.WINNER_PLAYER_2

        if self._state == GameState.ACTIVE and self._check_tie():
            self._state = GameState.TIE
        return self._state

    def _check_tie(self) -> bool:
        for row, col in itertools.product(list(range(self._board.shape[0])), list(range(self._board.shape[1]))):
            if GameToken.from_val(self._board[row][col]) == GameToken.EMPTY:
                return False
        return True

    def _check_diag_down(self, row, col) -> GameToken:
        if row + 4 > self._board.shape[0] or col - 3 < 0:
            return GameToken.EMPTY

        last_token = None
        for x, y in zip(range(0, 4), range(0, 4)):
            token = GameToken.from_val(self._board[row + x][col - y])
            if token == GameToken.EMPTY:
                return GameToken.EMPTY
            elif last_token and token != last_token:
                return GameToken.EMPTY
            else:
                last_token = token
        return last_token

    def _check_diag_up(self, row, col) -> GameToken:
        if row + 4 > self._board.shape[0] or col + 4 > self._board.shape[1]:
            return GameToken.EMPTY

        last_token = None
        for x, y in zip(range(0, 4), range(0, 4)):
            token = GameToken.from_val(self._board[row + x][col + y])
            if token == GameToken.EMPTY:
                return GameToken.EMPTY
            elif last_token and token != last_token:
                return GameToken.EMPTY
            else:
                last_token = token
        return last_token

    def _check_row(self, row) -> GameToken:
        last_token = GameToken.EMPTY
        longest_streak = 0
        for tok in self._board[:, row]:
            if tok != GameToken.EMPTY.value and tok != last_token.value:
                last_token = GameToken.from_val(tok)
                longest_streak = 1
            elif tok != GameToken.EMPTY.value:
                longest_streak += 1
            elif tok == GameToken.EMPTY.value:
                last_token = GameToken.EMPTY
                longest_streak = 0
                
            if longest_streak == self.sequence:
                return last_token
        return GameToken.EMPTY

    def _check_col(self, col) -> GameToken:
        last_token = GameToken.EMPTY
        longest_streak = 0
        for tok in self._board[col]:
            if tok == GameToken.EMPTY.value:
                return GameToken.EMPTY
            elif tok != last_token.value:
                last_token = GameToken.from_val(tok)
                longest_streak = 1
            else:
                longest_streak += 1

            if longest_streak == self.sequence:
                return last_token
        return GameToken.EMPTY
