import json
from http import HTTPStatus
from typing import Dict, Iterable

from flask import Response, request, Flask

from guacamole.xo.game import GameController


class FlaskRule:

    def __init__(self, rule, endpoint, function, methods: Iterable[str] = None):
        self._rule = rule
        self._endpoint = endpoint
        self._function = function
        self._methods = methods if methods else ['GET']

    def as_args(self) -> Dict:
        return {
            'rule': self._rule,
            'endpoint': self._endpoint,
            'view_func': self._function,
            'methods': [str(m) for m in self._methods]
        }


class GameServer:

    def __init__(self, host, port):
        self._game_controller = GameController()
        self._player_count = 0
        self._app = Flask('TicTacToe')
        self._host, self._port = host, port

    def start(self):
        for url_rule in self.get_url_rules():
            self._app.add_url_rule(**url_rule.as_args())
        self._app.run(host=self._host, port=self._port, debug=False, use_reloader=False, threaded=True)

    def get_url_rules(self) -> Iterable[FlaskRule]:
        return [
            FlaskRule('/restart', '/restart', self.restart),
            FlaskRule('/isReady', '/isReady', self.is_ready),
            FlaskRule('/getPlayerId', '/getPlayerId', self.get_player_id),
            FlaskRule('/nextMove', '/nextMove', self.next_move),
            FlaskRule('/winner', '/winner', self.winner),
            FlaskRule('/isTie', '/isTie', self.is_tie),
            FlaskRule('/state', '/state', self.state),
            FlaskRule('/isPlayerTurn', '/isPlayerTurn', self.player_turn)
        ]

    def is_ready(self):
        return Response(
            json.dumps({'isReady': self._player_count >= len(self._game_controller.players)}),
            status=HTTPStatus.OK
        )

    def restart(self):
        self._player_count = 0
        self._game_controller = GameController()
        return Response(json.dumps({'state': 'ok'}), status=HTTPStatus.OK)

    def get_player_id(self):
        if self._player_count >= len(self._game_controller.players):
            return Response(json.dumps({'playerId': None}), status=HTTPStatus.BAD_REQUEST)
        player_id = self._game_controller.players[self._player_count]
        self._player_count += 1
        return Response(
            json.dumps({'playerId': player_id, 'token': str(self._game_controller.token(player_id))}),
            status=HTTPStatus.OK)

    def next_move(self):
        player_id = request.args.get('playerId', None)
        x = request.args.get('x', None)
        y = request.args.get('y', None)
        if not player_id or not x or not y:
            return Response('no', status=HTTPStatus.BAD_REQUEST)
        action = self._game_controller.do_move(player_id, int(x), int(y))
        return Response(json.dumps({'result': action.value}), status=HTTPStatus.OK)

    def player_turn(self):
        player_id = request.args.get('playerId', None)
        if not player_id:
            return Response({'isTurn': False}, status=HTTPStatus.BAD_REQUEST)

        return Response(json.dumps({'isTurn': player_id == self._game_controller.current_player}), status=HTTPStatus.OK)

    def winner(self):
        return Response(json.dumps({'playerId': self._game_controller.winner}), status=HTTPStatus.OK)

    def is_tie(self):
        return Response(json.dumps({'isTie': self._game_controller.is_tie}), status=HTTPStatus.OK)

    def state(self):
        if not self._game_controller.state:
            return Response(json.dumps({'state': None}), status=HTTPStatus.OK)
        return Response(json.dumps({'state': self._game_controller.state.encode()}), status=HTTPStatus.OK)
