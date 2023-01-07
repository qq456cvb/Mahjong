#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame
import collections
import sprites
import resource
from enum import Enum
import numpy as np
import pickle
from build.Release.clib import TILE_TYPE


class Player:
    complete_keys = pickle.load(open('complete.pickle', 'rb'))

    class POSITION(Enum):
        EAST = 1
        SOUTH = 2
        WEST = 3
        NORTH = 4

    def __init__(self, graphics, pos, name):
        self._name = name
        self._tiles = []
        self._cnt = np.zeros([34])
        self._graphics = graphics
        self._pos = pos

    def reset(self):
        self._tiles.clear()
        self._cnt = np.zeros([34])

    def add(self, tiles):
        if isinstance(tiles, collections.Iterable):
            for tile in tiles:
                self.add(tile)
        else:
            self._tiles.append(tiles)

            self._cnt[int(tiles)] += 1
            self._tiles.sort(key=lambda x: int(x))

    def refresh(self):
        self._graphics.clear_player_sprites(self)
        x, y = self._graphics._width // 6, self._graphics._height // 8 * 7
        tmp = dict()
        for tile in self._tiles:
            if isinstance(self, HumanPlayer):
                def on_click(a):
                    if not a.clicked:
                        a.rect.y -= 20
                        a.clicked = True
                        self._chosen_tiles.append(tmp[a])
                        # print(tmp[a])
                    else:
                        a.rect.y += 20
                        a.clicked = False
                        self._chosen_tiles.remove(tmp[a])
                        # print(tmp[a])
                tmp[self._graphics.add_player_sprite_by_type(self, tile, (x, y), on_click=on_click, clicked=False)] = tile
            else:
                self._graphics.add_player_sprite_by_type(self, tile, (x, y))
            x += 40

    def remove(self, tiles):
        if isinstance(tiles, collections.Iterable):
            for tile in tiles:
                self.remove(tile)
            return tiles
        else:
            self._tiles.remove(tiles)
            self._cnt[int(tiles)] -= 1
            return tiles

    def can_complete(self, tile=TILE_TYPE.NONE):
        cnt = self._cnt.copy()
        if tile != TILE_TYPE.NONE:
            cnt[int(tile)] += 1
        b = False
        x = 0
        p = -1
        for i in range(3):
            for j in range(9):
                if cnt[i * 9 + j] == 0:
                    if b:
                        b = False
                        x |= 0x1 << p
                        p += 1
                else:
                    p += 1
                    b = True
                    if cnt[i * 9 + j] == 2:
                        x |= 0x3 << p
                        p += 2
                    elif cnt[i * 9 + j] == 3:
                        x |= 0xf << p
                        p += 4
                    elif cnt[i * 9 + j] == 4:
                        x |= 0x3f << p
                        p += 6
            if b:
                b = False
                x |= 0x1 << p
                p += 1
        for i in range(27, 34):
            if cnt[i] > 0:
                p += 1
                if cnt[i] == 2:
                    x |= 0x3 << p
                    p += 2
                elif cnt[i] == 3:
                    x |= 0xf << p
                    p += 4
                elif cnt[i] == 4:
                    x |= 0x3f << p
                    p += 6
                x |= 0x1 << p
                p += 1
        return x in Player.complete_keys

    def can_chow(self, tile):
        if tile == TILE_TYPE.NONE:
            return False, None
        cnt = self._cnt
        arr = [[-2, -1], [-1, 1], [1, 2]]
        # print(cnt)

        can_chow = False
        sols = []
        for bound in range(9, 28, 9):
            if bound - 9 <= int(tile) <= bound:
                for i in range(3):
                    val = int(tile) + arr[i][0], int(tile) + arr[i][1]
                    if val[0] >= bound - 9 and val[1] < bound and cnt[val[0]] >= 1 and cnt[val[1]] >= 1:
                        can_chow = True
                        sols.append([TILE_TYPE(val[0]), TILE_TYPE(val[1])])
        return can_chow, sols

    def can_pung(self, tile):

        return self._cnt[int(tile)] >= 2

    def respond_normal(self):
        pass

    def respond_chow(self, tile):
        pass

    def respond_complete(self, tile=None):
        pass

    def respond_pung(self, tile):
        pass


class HumanPlayer(Player):
    def __init__(self, graphics, pos, name):
        Player.__init__(self, graphics, pos, name)
        self._chosen_tiles = []

    def reset(self):
        super().reset()
        self._chosen_tiles = []

    def respond_normal(self):
        clicked = False
        btn = sprites.Button((255, 0, 0), 100, 30)
        btn.rect.x = 300
        btn.rect.y = 600

        txt = sprites.Text(u'请出牌', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])

        def on_click():
            if btn.alive():
                nonlocal clicked, txt
                if len(self._chosen_tiles) != 1:
                    # txt = u'请出一张牌'
                    txt.kill()
                    txt = sprites.Text(u'请出一张牌', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])
                    self._graphics.add_sprite(txt)
                    return
                btn.kill()
                clicked = True
                txt.kill()

        self._graphics.add_sprite(btn)
        self._graphics.add_sprite(txt)

        btn.on_click = on_click
        while not clicked:
            self._graphics.clear()
            self._graphics.draw_all()
            # self._graphics.show_text(txt)
            pygame.display.update()
            self._graphics.handle(pygame.event.get())
            self._graphics.clock.tick(30)
        tile = self._chosen_tiles[0]
        self.remove(tile)
        self._chosen_tiles.clear()
        self.refresh()
        return tile

    def respond_chow(self, tile):
        can_chow, sols = self.can_chow(tile)
        if can_chow:
            clicked = False
            btn = sprites.Button((255, 0, 0), 100, 30)
            btn.rect.x = 300
            btn.rect.y = 600

            # txt = u'要吃吗'
            txt = sprites.Text(u'要吃吗', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])

            def on_click():
                if btn.alive():

                    nonlocal clicked, txt, sols
                    if len(self._chosen_tiles) == 0:
                        btn.kill()
                        txt.kill()
                        clicked = True
                        return
                    for sol in sols:
                        if sorted(self._chosen_tiles, key=lambda x: int(x)) == sorted(sol, key=lambda x: int(x)):
                            btn.kill()
                            txt.kill()
                            clicked = True
                            return
                    txt.kill()
                    txt = sprites.Text(u'出牌不符合规定', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])
                    self._graphics.add_sprite(txt)
                    # txt = u'出牌不符合规定'

            self._graphics.add_sprite(btn)
            self._graphics.add_sprite(txt)

            btn.on_click = on_click
            while not clicked:
                self._graphics.clear()
                self._graphics.draw_all()
                # self._graphics.show_text(txt)
                pygame.display.update()
                self._graphics.handle(pygame.event.get())
                self._graphics.clock.tick(30)
            if len(self._chosen_tiles) > 0:
                self.remove(self._chosen_tiles)
                self._chosen_tiles.clear()
                self.refresh()
                return True
        return False

    def respond_complete(self, tile=TILE_TYPE.NONE):
        can_complete = self.can_complete(tile)
        if can_complete:
            clicked = False
            btn_yes = sprites.Button((0, 255, 0), 100, 30)
            btn_yes.rect.x = 300
            btn_yes.rect.y = 600

            btn_no = sprites.Button((255, 0, 0), 100, 30)
            btn_no.rect.x = 500
            btn_no.rect.y = 600

            txt = sprites.Text(u'要胡吗', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])
            response = False

            def on_click_yes():
                if btn_yes.alive():
                    nonlocal response, clicked
                    btn_yes.kill()
                    clicked = True
                    txt.kill()
                    response = True

            def on_click_no():
                if btn_no.alive():
                    nonlocal response, clicked
                    btn_no.kill()
                    txt.kill()
                    clicked = True
                    response = False

            self._graphics.add_sprite(btn_yes)
            self._graphics.add_sprite(btn_no)
            self._graphics.add_sprite(txt)

            btn_yes.on_click = on_click_yes
            btn_no.on_click = on_click_no
            while not clicked:
                self._graphics.clear()
                self._graphics.draw_all()
                pygame.display.update()
                self._graphics.handle(pygame.event.get())
                self._graphics.clock.tick(30)

            self._graphics.clear()
            self._graphics.draw_all()
            return response
        else:
            return False

    def respond_pung(self, tile):
        can_pung = self.can_pung(tile)

        if can_pung:
            print(tile)
            print(self._tiles)
            print(self._cnt)
            clicked = False
            btn = sprites.Button((255, 0, 0), 100, 30)
            btn.rect.x = 300
            btn.rect.y = 600

            txt = sprites.Text(u'要碰吗', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])

            def on_click():
                if btn.alive():

                    nonlocal clicked, txt
                    if len(self._chosen_tiles) == 0:
                        btn.kill()
                        txt.kill()
                        clicked = True
                        return
                    if len(self._chosen_tiles) == 2 and int(self._chosen_tiles[0]) == int(self._chosen_tiles[1]) == int(tile):
                        btn.kill()
                        txt.kill()
                        clicked = True
                        return

                    txt.kill()
                    txt = sprites.Text(u'出牌不符合规定', [self._graphics._width / 2 - 60, self._graphics._height / 2 - 15])
                    self._graphics.add_sprite(txt)

            self._graphics.add_sprite(btn)
            self._graphics.add_sprite(txt)

            btn.on_click = on_click
            while not clicked:
                self._graphics.clear()
                self._graphics.draw_all()
                pygame.display.update()
                self._graphics.handle(pygame.event.get())
                self._graphics.clock.tick(30)
            if len(self._chosen_tiles) > 0:
                self.remove(self._chosen_tiles)
                self._chosen_tiles.clear()
                self.refresh()
                return True
        return False


class AIPlayer(Player):
    def __init__(self, graphics, pos, name):
        Player.__init__(self, graphics, pos, name)

    def respond_normal(self):
        ret = self.remove(self._tiles[0])
        self.refresh()
        return ret

    def respond_chow(self, tile):
        # ret = self.remove(self._tiles[0])
        # self.refresh()
        return False

    def respond_complete(self, tile=None):
        pass

    def respond_pung(self, tile):
        return False


if __name__ == '__main__':
    player = Player(None, None, 'nihao')
    # player.add([TILE_TYPE.BAMBOO_ONE, TILE_TYPE.BAMBOO_ONE])
    # print(player._cnt)
    # print(player.can_complete())
    player.add([TILE_TYPE.BAMBOO_ONE, TILE_TYPE.BAMBOO_ONE, TILE_TYPE.BAMBOO_ONE,
                     TILE_TYPE.BAMBOO_TWO, TILE_TYPE.BAMBOO_THREE, TILE_TYPE.BAMBOO_FOUR,
                     TILE_TYPE.BAMBOO_FIVE,
                     TILE_TYPE.BAMBOO_SIX, TILE_TYPE.BAMBOO_SEVEN, TILE_TYPE.SPECIAL_EAST,
                     TILE_TYPE.SPECIAL_EAST,
                     TILE_TYPE.SPECIAL_EAST, TILE_TYPE.SPECIAL_WEST, TILE_TYPE.SPECIAL_WEST])
    print(player._cnt)
    print(player.can_complete())
    # print('#08X' % player.can_complete())