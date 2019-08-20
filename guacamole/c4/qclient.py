import os
import pickle
import random
from collections import deque
from pathlib import Path

from guacamole.c4.client import GameClient
from guacamole.c4.game import GameToken, GameStateController


class QClient(GameClient):

    def __init__(self, controller: GameStateController, token: GameToken, exploration=0.05, learning_rate=0.05,
                 discount_factor=1.00, save_path=None):
        super().__init__(controller, token)
        self._policy = dict()
        self.exploration, self.alpha, self.gamma = exploration, learning_rate, discount_factor
        self._action_sequence = deque()
        self.save_path = save_path

    def load(self) -> bool:
        if not Path(self.save_path).exists():
            return False
        with open(self.save_path, 'rb') as mf:
            self._policy = pickle.load(mf)
        return True

    def save(self):
        os.makedirs(os.path.split(self.save_path)[0], exist_ok=True)
        with open(self.save_path, 'wb') as mf:
            pickle.dump(self._policy, file=mf)

    def provide_action(self) -> int:
        rows = self.controller.encode()
        state = list()
        for row in rows:
            state.extend(row)
        state = ''.join(str(x) for x in state)

        if random.random() < self.exploration:
            action = random.randint(0, self.controller.size() - 1)
            self._action_sequence.append((state, action))
            return action

        values = self._policy.get(state, None)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy[state] = values

        action = max(range(self.controller.size()), key=lambda i: values[i])
        self._action_sequence.append((state, action))
        return action

    def bad_move(self):
        state, action = self._action_sequence.popleft()

        values = self._policy.get(state, None)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy[state] = values

        values[action] = -1

    def lost(self):
        self._update_with_reward(-1)

    def won(self):
        self._update_with_reward(1)

    def tie(self):
        self._update_with_reward(0.5)

    def _update_with_reward(self, reward: float):
        state, action = self._action_sequence.popleft()

        values = self._policy.get(state, None)
        if not values:
            values = [random.random() for _ in range(self.controller.size())]
            self._policy[state] = values

        values[action] += (1 - self.alpha) * values[action] + self.alpha * reward

        max_prev = self.gamma * max(values)
        while len(self._action_sequence) > 0:
            state, action = self._action_sequence.popleft()
            values = self._policy.get(state, None)
            if not values:
                values = [random.random() for _ in range(self.controller.size())]
                self._policy[state] = values

            values[action] = (1 - self.alpha) * values[action] + self.alpha * max_prev
            max_prev = self.gamma * max(values)
