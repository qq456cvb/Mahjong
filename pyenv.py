
import resource
import random
from players import Player
import copy
import itertools
from montecarlo import MCTree


class ACTION_TYPE:
    DISCARD = 0
    CHOW = 1
    PUNG = 2


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


# class MCPlayer(Player):
#     def __init__(self, name, env):
#         Player.__init__(self, None, None, name)
#         self.env = env
#
#     def respond_chow(self, tile):
#
#
#     def respond_pung(self, tile):
#         if self.can_pung(tile):
#             self.remove([tile, tile])
#             return True
#         return False
#
#     def respond_normal(self):
#         return self.remove(random.choice(self._tiles))
#
#     def respond_complete(self, tile=None):
#         return self.can_complete(tile)



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
        self._control_player = 0
        self._all_tiles = []
        self._run = self.run()
        self._searching = False

    def reset(self):
        self._run = self.run()
        self._last_tile = None
        self._searching = False
        self._all_tiles = Env.ALL_TILES.copy()
        random.shuffle(self._all_tiles)
        for player in self._players:
            player.reset()
            player.add(self._all_tiles[:13])
            self._all_tiles = self._all_tiles[13:]

    # def step(self, draw=True):
    #     # cards all out
    #     if len(self._all_tiles) == 0:
    #         self.reset()
    #         return -1, True
    #
    #     if draw:
    #         self._players[self._current_turn].add(self._all_tiles.pop(0))
    #         if self._players[self._current_turn].respond_complete():
    #             self.reset()
    #             return self._current_turn, True
    #
    #     self._last_tile = self._players[self._current_turn].respond_normal()
    #     for i in range(self._current_turn + 1, self._current_turn + 4):
    #         if self._players[i % 4].respond_complete(self._last_tile):
    #             self.reset()
    #             return i % 4, True
    #
    #     for i in range(self._current_turn + 1, self._current_turn + 4):
    #         if self._players[i % 4].respond_pung(self._last_tile):
    #             self._current_turn = i % 4
    #             self._last_tile = None
    #             return self.step(False)
    #
    #     self._current_turn = (self._current_turn + 1) % 4
    #     return self._current_turn, False

    def run(self):
        draw = True
        while True:
            # cards all out
            if len(self._all_tiles) == 0:
                self.reset()
                return -1, True

            if self._last_tile:
                yield self._current_turn, ACTION_TYPE.CHOW
                if not self._searching and self._current_turn == self._control_player:
                    mc = MCTree(self, self._control_player, ACTION_TYPE.CHOW)
                    mc.search(4, 100)
                    a = mc.predict(0.5)

                    def foo(_):
                        self._players[self._current_turn].remove(a)
                        return True

                    self._players[self._current_turn].respond_chow = foo if a is not None else lambda _: False
                if self._players[self._current_turn].respond_chow(self._last_tile):
                    draw = False
                    continue

            if draw:
                self._players[self._current_turn].add(self._all_tiles.pop(0))
                if self._players[self._current_turn].respond_complete():
                    self.reset()
                    return self._current_turn, True

            yield self._current_turn, ACTION_TYPE.DISCARD
            if not self._searching and self._current_turn == self._control_player:
                mc = MCTree(self, self._current_turn, ACTION_TYPE.CHOW)
                mc.search(4, 100)
                a = mc.predict(0.5)
                self._players[self._current_turn].respond_normal = lambda: self._players[self._current_turn].remove(self._players[self._current_turn]._tiles[a])
            self._last_tile = self._players[self._current_turn].respond_normal()
            for i in range(self._current_turn + 1, self._current_turn + 4):
                if self._players[i % 4].respond_complete(self._last_tile):
                    self.reset()
                    return i % 4, True

            jump_turn = False
            for i in range(self._current_turn + 1, self._current_turn + 4):
                yield i, ACTION_TYPE.PUNG
                if not self._searching and i == self._control_player:
                    mc = MCTree(self, i, ACTION_TYPE.CHOW)
                    mc.search(4, 100)
                    a = mc.predict(0.5)

                    def foo(tile):
                        self._players[i].remove([tile, tile])
                        return True

                    self._players[i].respond_pung = foo if a else lambda _: False
                if self._players[i % 4].respond_pung(self._last_tile):
                    self._current_turn = i % 4
                    self._last_tile = None
                    jump_turn = True
                    draw = False
                    break

            if jump_turn:
                continue

            self._current_turn = (self._current_turn + 1) % 4
            draw = True

    def step(self, idx, a_type, a):
        if a_type == ACTION_TYPE.DISCARD:
            self._players[idx].respond_normal = lambda: self._players[idx].remove(self._players[idx]._tiles[a])
        elif a_type == ACTION_TYPE.CHOW:
            def foo(_):
                self._players[idx].remove(a)
                return True
            self._players[idx].respond_chow = foo if a is not None else lambda _: False
        elif a_type == ACTION_TYPE.PUNG:
            def foo(tile):
                self._players[idx].remove([tile, tile])
                return True
            self._players[idx].respond_pung = foo if a else lambda _: False

        r = 0
        a_type = None
        try:
            current_player = -1
            while current_player != idx:
                current_player, a_type = next(self._run)
            done = False
        except StopIteration as e:
            winner = e.value[0]
            if winner == idx:
                r = 1
            elif winner == -1:
                r = 0
            else:
                r = -1
            done = True
        return r, done, a_type

    def get_action_space(self, idx, a_type):
        if a_type == ACTION_TYPE.DISCARD:
            return list(range(len(self._players[idx]._tiles)))
        elif a_type == ACTION_TYPE.CHOW:
            can_chew, sols = self._players[idx].can_chow(self._last_tile)
            return [None, *sols] if can_chew else [None]
        elif a_type == ACTION_TYPE.PUNG:
            can_pung = self._players[idx].can_pung(self._last_tile)
            return [False, True] if can_pung else [False]


if __name__ == '__main__':
    env = Env()

    cnts = [0 for i in range(5)]
    for i in range(1):
        env.reset()
        done = False
        winner = 0
        try:
            while True:
                next(env._run)
        except StopIteration as e:
            winner = e.value[0]
        if winner == -1:
            cnts[0] += 1
        else:
            cnts[winner + 1] += 1

    for i in range(5):
        print(cnts[i] / 1)

