import pygame
import sprites
import players
import math
import six
import functools


def get_rot_by_player_pos(pos):
    rot = 0
    if pos == players.Player.POSITION.SOUTH:
        rot = 0
    elif pos == players.Player.POSITION.NORTH:
        rot = 180
    elif pos == players.Player.POSITION.WEST:
        rot = 270
    elif pos == players.Player.POSITION.EAST:
        rot = 90
    return rot


def rotate_rect(rect, rot, c):

    center = rect.x + rect.width / 2 - c[0], rect.y + rect.height / 2 - c[1]
    rotate_center = math.cos(rot / 180 * math.pi) * center[0] + math.sin(rot / 180 * math.pi) * center[1] + c[0], \
                    -math.sin(rot / 180 * math.pi) * center[0] + math.cos(rot / 180 * math.pi) * center[1] + c[1]
    if rot % 180 == 90:
        return pygame.Rect(rotate_center[0] - rect.height / 2, rotate_center[1] - rect.width / 2, rect.height, rect.width)
    else:
        return pygame.Rect(rotate_center[0] - rect.width / 2, rotate_center[1] - rect.height / 2, rect.width, rect.height)


__all__ = ['Graphics']


class Graphics:
    def __init__(self, src_mgr):
        self._resource_mgr = src_mgr
        self._width, self._height = 800, 800
        self._screen = pygame.display.set_mode((self._width, self._height))
        self._layers = dict()
        # self._layer.fill((255, 0, 0))

        self._player_sprites = dict()
        self._other_sprites = pygame.sprite.OrderedUpdates()
        self._cached_out_tile = dict()
        pygame.font.init()
        self._font = pygame.font.SysFont('wenquanyimicroheimono', 30)
        # for _, src in self._resource_mgr.resources.items():
        #     self._all_sprites.add(sprites.Tile(src))

    def show_text(self, txt, pos=None):
        if not pos:
            pos = (self._width / 2 - 60, self._height / 2 - 15)
        surf = self._font.render(txt, True, (0, 204, 102))
        self._screen.blit(surf, pos)

    def catch_players(self, players):
        for player in players:
            self._player_sprites[player] = pygame.sprite.OrderedUpdates()
            self._layers[player] = pygame.Surface((self._width, self._height), pygame.SRCALPHA, 32)
            self._layers[player].convert_alpha()

    def reset(self):
        for _, sprites in self._player_sprites.items():
            sprites.empty()
        self._other_sprites = pygame.sprite.Group()

    def clear_player_sprites(self, player):
        if player in self._player_sprites:
            self._player_sprites[player].empty()

    def add_player_sprite_by_type(self, player, t, pos=(0, 0), **kwargs):
        tile = sprites.Tile(self._resource_mgr.resources[t] if (isinstance(player, players.HumanPlayer) or ('draw' in kwargs and kwargs['draw'])) else self._resource_mgr.resources['hidden'], t)
        tile.rect.x = pos[0]
        tile.rect.y = pos[1]
        for k, v in six.iteritems(kwargs):
            setattr(tile, k, v)
            if k == 'on_click':
                tile.on_click = functools.partial(v, tile)
        tile.rot = get_rot_by_player_pos(player._pos)
        self._player_sprites[player].add(tile)
        return tile

    def add_player_sprite(self, player, sprite):
        self._player_sprites[player].add(sprite)

    def remove_player_sprite_by_type(self, player, t):
        if player not in self._player_sprites:
            raise Exception('player not found')
        to_del = None
        for sprite in self._player_sprites[player]:
            if sprite._type == t:
                to_del = sprite
                break
        self._player_sprites[player].remove(to_del)

    def draw_player_sprites(self, player):
        if player not in self._player_sprites:
            raise Exception('player not found')

        self._player_sprites[player].draw(self._layers[player])
        rot = get_rot_by_player_pos(player._pos)
        rot_surf = pygame.transform.rotate(self._layers[player], rot)
        self._screen.blit(rot_surf, (0, 0))

    def add_sprite(self, sprite):
        self._other_sprites.add(sprite)

    def clear(self):
        self._screen.fill((255, 255, 255))
        for layer in self._layers:
            self._layers[layer].fill((255, 255, 255, 0))

    def draw_all(self):
        for player in self._player_sprites:
            self.draw_player_sprites(player)
        self.draw_others()

    def draw_others(self):
        self._other_sprites.draw(self._screen)

    def handle(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()

                for s in self._other_sprites:
                    if s.rect.collidepoint(pos) and hasattr(s, 'on_click'):
                        s.on_click()
                for player in self._player_sprites:
                    for s in self._player_sprites[player]:
                        if rotate_rect(s.rect, s.rot, (self._width / 2, self._height / 2)).collidepoint(pos) and hasattr(s, 'on_click'):
                            s.on_click()
            if event.type == pygame.QUIT:
                return True
        return False
