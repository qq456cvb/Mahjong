
import resource
import random
from players import Player


class RandomPlayer(Player):
    def __init__(self, name):
        Player.__init__(self, None, None, name)

    def respond_chow(self, tile):
        can_chow, sols = self.can_chow(tile)
        if can_chow:
            self.remove(random.choice(sols))
            return True
        return False

    def respond_pung(self, tile):
        if self.can_pung(tile):
            self.remove([tile, tile])
            return True
        return False

    def respond_normal(self):
        return self.remove(random.choice(self._tiles))

    def respond_complete(self, tile=None):
        return self.can_complete(tile)


class Env:
    ALL_TILES = []
    for i in resource.TileType.BAMBOO:
        ALL_TILES.extend([[i]] * 4)
    for i in resource.TileType.CIRCLE:
        ALL_TILES.extend([[i]] * 4)
    for i in resource.TileType.WAN:
        ALL_TILES.extend([[i]] * 4)
    for i in resource.TileType.SPECIAL:
        ALL_TILES.extend([[i]] * 4)

    def __init__(self):
        self._current_turn = 0
        self._players = [RandomPlayer('player %d' % i) for i in range(4)]
        self._last_tile = None
        self._all_tiles = []

    def reset(self):

        self._last_tile = None
        self._all_tiles = Env.ALL_TILES.copy()
        random.shuffle(self._all_tiles)
        for player in self._players:
            player.reset()
            player.add(self._all_tiles[:13])
            self._all_tiles = self._all_tiles[13:]

    def step(self, draw=True):
        # cards all out
        if len(self._all_tiles) == 0:
            self.reset()
            return -1, True

        if draw:
            self._players[self._current_turn].add(self._all_tiles.pop(0))
            if self._players[self._current_turn].respond_complete():
                self.reset()
                return self._current_turn, True

        self._last_tile = self._players[self._current_turn].respond_normal()
        for i in range(self._current_turn + 1, self._current_turn + 4):
            if self._players[i % 4].respond_complete(self._last_tile):
                self.reset()
                return i % 4, True

        for i in range(self._current_turn + 1, self._current_turn + 4):
            if self._players[i % 4].respond_pung(self._last_tile):
                self._current_turn = i % 4
                self._last_tile = None
                return self.step(False)

        self._current_turn = (self._current_turn + 1) % 4
        return self._current_turn, False


if __name__ == '__main__':
    env = Env()
    cnts = [0 for i in range(5)]
    for i in range(1000):
        env.reset()
        done = False
        winner = 0
        while not done:
            winner, done = env.step()
        if winner == -1:
            cnts[0] += 1
        else:
            cnts[winner + 1] += 1

    for i in range(5):
        print(cnts[i] / 1000)

