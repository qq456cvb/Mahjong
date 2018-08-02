import pygame
import resource
import graphics
import players
import random
import os
import sprites
from clib import TILE_TYPE


class Controller():
    def __init__(self, src_dir):
        resource_mgr = resource.Resource()
        resource_mgr.load(src_dir)
        self._graphic_mgr = graphics.Graphics(resource_mgr)
        self._last_tick = 0
        self._current_turn = 0
        self._last_tile = None
        self._all_tiles = []
        self._clock = pygame.time.Clock()
        self._players = [players.HumanPlayer(self._graphic_mgr, players.Player.POSITION.SOUTH, u'南大'),
                         players.AIPlayer(self._graphic_mgr, players.Player.POSITION.EAST, u'东大'),
                         players.AIPlayer(self._graphic_mgr, players.Player.POSITION.NORTH, u'北大'),
                         players.AIPlayer(self._graphic_mgr, players.Player.POSITION.WEST, u'西大')]
        self._graphic_mgr.catch_players(self._players)
        self._graphic_mgr.clock = self._clock
        self._can_draw = False
        self._cache_text = None
        self.reset()

    def reset(self):
        self._current_turn = 0
        self._last_tile = TILE_TYPE.NONE
        self._can_draw = False
        self._cache_text = None
        self._all_tiles = []
        self._graphic_mgr.reset()
        for _ in range(4):
            self._all_tiles.extend([TILE_TYPE(i) for i in range(34)])
        random.shuffle(self._all_tiles)
        for player in self._players:
            player.reset()
            player.add(self._all_tiles[:13])
            self._all_tiles = self._all_tiles[13:]
        # self._players[0].add(self._all_tiles.pop(0))
        for player in self._players:
            player.refresh()

    def step(self, draw=True):
        if len(self._all_tiles) == 0:
            self._graphic_mgr.show_text(u'游戏结束')
            pygame.display.update()
            self._clock.tick(0.5)
            self.reset()
            return

        if self._players[self._current_turn].respond_chow(self._last_tile):
            return self.step(False)

        if draw:
            self._players[self._current_turn].add(self._all_tiles.pop(0))
            self._players[self._current_turn].refresh()
            if self._players[self._current_turn].respond_complete():
                self.reset()
                self._graphic_mgr.show_text(u'游戏结束')
                pygame.display.update()
                self._clock.tick(0.5)
                return

        self._last_tile = self._players[self._current_turn].respond_normal()

        # self._last_tile = self._players[self._current_turn].remove(self._players[self._current_turn]._tiles[0])

        self._graphic_mgr.add_player_sprite_by_type(self._players[self._current_turn], self._last_tile, (self._graphic_mgr._width // 2, self._graphic_mgr._height // 8 * 6), draw=True)
        if self._cache_text and self._cache_text.alive():
            self._cache_text.kill()
        self._cache_text = sprites.Text(u'%s 出了牌' % self._players[self._current_turn]._name, [self._graphic_mgr._width / 2 - 60, self._graphic_mgr._height / 2 - 75])
        self._graphic_mgr.add_sprite(self._cache_text)
        for i in range(self._current_turn + 1, self._current_turn + 4):
            if self._players[i % 4].respond_complete(self._last_tile):
                self.reset()
                self._graphic_mgr.show_text(u'游戏结束')
                pygame.display.update()
                self._clock.tick(0.5)
                return
        for i in range(self._current_turn + 1, self._current_turn + 4):
            if self._players[i % 4].respond_pung(self._last_tile):
                self._current_turn = i % 4
                self._last_tile = TILE_TYPE.NONE
                return self.step(False)

        self._current_turn = (self._current_turn + 1) % 4

    def run(self, events):
        self._graphic_mgr.clear()
        self._graphic_mgr.draw_others()
        for player in self._players:
            self._graphic_mgr.draw_player_sprites(player)
        if self._graphic_mgr.handle(events):
            pygame.quit()
        # rot_surf = pygame.transform.rotate(self._graphic_mgr._layer, 90)
        # self._graphic_mgr._screen.blit(rot_surf, (0, 0))

        self.step()
        self._clock.tick(30)


if __name__ == '__main__':
    # print(pygame.font.get_fonts())
    ctrlr = Controller('./tiles')

    pygame.init()
    done = False
    while True:
        ctrlr.run(pygame.event.get())
        pygame.display.flip()
