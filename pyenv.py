
import resource
from players import Player


class RandomPlayer(Player):
    def __init__(self, name):
        Player.__init__(self, None, None, name)

    def respond_chow(self, tile):

    def respond_pung(self, tile):


    def respond_normal(self):

    def respond_complete(self, tile=None):



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
        for player in self._players:
            player.reset()

        self._last_tile = None
        self.