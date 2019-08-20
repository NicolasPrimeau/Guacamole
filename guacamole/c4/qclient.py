import json
import os
import random
from collections import deque, Iterable
from pathlib import Path
from typing import List

from guacamole.c4.client import GameClient
from guacamole.c4.game import GameToken, GameStateController


class TreeDict:

    def __init__(self, root: dict = None):
        self.root = dict() if not root else root

    def set(self, state: Iterable[int], value: List[float]):
        node = self._get_node(state)
        node['vals'] = value

    def get(self, state: Iterable[int]):
        node = self._get_node(state)
        return node.get('vals', None)

    def __contains__(self, item):
        return self.get(item) is not None

    def _get_node(self, state):
        node = self.root
        for child_id in state:
            if child_id not in node:
                node[child_id] = dict()
            node = node[child_id]
        return node


class QClient(GameClient):

    def __init__(self, controller: GameStateController, token: GameToken, exploration=0.05, learning_rate=0.05,
                 discount_factor=1.00, save_path=None):
        super().__init__(controller, token)
        self._policy = TreeDict()
        self.exploration, self.alpha, self.gamma = exploration, learning_rate, discount_factor
        self._action_sequence = deque()
        self.save_path = save_path

    def load(self):
        if not Path(self.save_path).exists():
            return
        with open(self.save_path, 'r') as mf:
            self._policy = TreeDict(json.load(mf))

    def save(self):
        os.makedirs(os.path.split(self.save_path)[0], exist_ok=True)
        with open(self.save_path, 'w') as mf:
            json.dump(self._policy.root, fp=mf)

    def provide_action(self) -> int:
        rows = self.controller.encode()
        state = list()
        for row in rows:
            state.extend(row)

        if random.random() < self.exploration:
            action = random.randint(0, self.controller.size() - 1)
            self._action_sequence.append((state, action))
            return action

        values = self._policy.get(state)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy.set(state, values)
        action = max(range(self.controller.size()), key=lambda i: values[i])
        self._action_sequence.append((state, action))
        return action

    def bad_move(self):
        state, action = self._action_sequence.popleft()

        values = self._policy.get(state)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy.set(state, values)

        values[action] = -1

    def lost(self):
        self._update_with_reward(-1)

    def won(self):
        self._update_with_reward(1)

    def tie(self):
        self._update_with_reward(0.5)

    def _update_with_reward(self, reward: float):

        state, action = self._action_sequence.popleft()

        values = self._policy.get(state)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy.set(state, values)

        values[action] += (1 - self.alpha) * values[action] + self.alpha * reward

        max_prev = self.gamma * max(values)
        while len(self._action_sequence) > 0:
            state, action = self._action_sequence.popleft()
            values = self._policy.get(state)
            if not values:
                values = [random.random() for _ in range(self.controller.size())]
                self._policy.set(state, values)

            values[action] = (1 - self.alpha) * values[action] + self.alpha * max_prev
            max_prev = self.gamma * max(values)
