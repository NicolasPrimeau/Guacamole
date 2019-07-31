import os
import time
from http import HTTPStatus
from typing import Optional

import requests

from guacamole.xo.game import GameAction, GameState


class GameClient:

    def __init__(self, host, port, poll_time_s=2, restart=False):
        self._player_id = None
        self._token = None
        self._hostname = 'http://{}:{}'.format(host, port)
        self._poll_time_s = poll_time_s
        if restart:
            self.restart()

    def start(self):
        if not self.connect():
            return

        while not self.is_ready():
            self.clear_terminal()
            print('Game not ready')
            time.sleep(self._poll_time_s)

        game_done = False
        winner_id = None
        while not game_done:
            if not self.is_current_turn():
                self.clear_terminal()
                print('Not your turn')
                self.print_board()
                winner_id = self.winner_id()
                game_done = winner_id is not None or self.is_tie()
                while not self.is_current_turn() and not game_done:
                    time.sleep(self._poll_time_s)
                    game_done = winner_id is not None or self.is_tie()

            if game_done:
                break

            self.clear_terminal()
            turn_done = False
            while not turn_done:
                self.print_board()
                try:
                    coords = input('Enter x, y: ')
                    x_str, y_str = coords.split(',')
                    x, y = int(x_str.lstrip().rstrip()), int(y_str.rstrip().lstrip())
                    result = self.do_move(x, y)
                    if result == GameAction.INVALID:
                        self.clear_terminal()
                        print('Invalid move')
                        turn_done = False
                    elif result == GameAction.WON:
                        turn_done = True
                        game_done = True
                        winner_id = self._player_id
                    elif result == GameAction.TIE:
                        turn_done = True
                        game_done = True
                    elif result == GameAction.NEXT:
                        turn_done = True
                except Exception as e:
                    print(e)
                    turn_done = False

        if winner_id == self._player_id:
            print('Yay you won')
        elif not winner_id:
            print('Nobody wins congrats')
        else:
            print('You lost so bad')

    @staticmethod
    def clear_terminal():
        os.system('cls' if os.name == 'nt' else 'clear')

    def restart(self):
        response = requests.get('{}/restart'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            return False
        return True

    def connect(self) -> bool:
        response = requests.get('{}/getPlayerId'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            return False
        self._player_id = response.json().get('playerId')
        self._token = response.json().get('token')
        if not self._player_id:
            print('Sorry, max player count')
            return False
        return True

    def is_ready(self) -> bool:
        response = requests.get('{}/isReady'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            return False
        return response.json().get('isReady', False)

    def is_current_turn(self) -> bool:
        response = requests.get('{}/isPlayerTurn'.format(self._hostname), params={'playerId': self._player_id})
        if response.status_code != HTTPStatus.OK:
            return False
        return response.json().get('isTurn', False)

    def do_move(self, x, y) -> GameAction:
        response = requests.get(
            '{}/nextMove'.format(self._hostname), params={'playerId': self._player_id, 'x': x, 'y': y})
        if response.status_code != HTTPStatus.OK:
            return GameAction.INVALID
        return GameAction.from_code(response.json().get('result', -1))

    def winner_id(self) -> Optional[str]:
        response = requests.get('{}/winner'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            return None
        return response.json().get('playerId', None)

    def is_tie(self) -> bool:
        response = requests.get('{}/isTie'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            return False
        return response.json().get('isTie', False)

    def print_board(self) -> bool:
        response = requests.get('{}/state'.format(self._hostname))
        if response.status_code != HTTPStatus.OK:
            print('Error printing board')
            return False

        encoded_state = response.json().get('state', None)
        if not encoded_state:
            print('Error printing board')
            return False

        print()
        print('You are {}'.format(self._token))
        print()
        state = GameState.decode(encoded_state)
        for x in range(state.x):
            for y in range(state.y):
                print(' {} '.format(str(state.get(x, y))), end='')
            print()
            print()
        print()
        print()
        return True
