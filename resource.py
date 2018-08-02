import glob
import os
import pygame
from enum import Enum
import sys
sys.path.insert(0, './build')
from clib import TILE_TYPE


# class TileType:
#
#     class BAMBOO(Enum):
#         ONE = 0
#         TWO = 1
#         THREE = 2
#         FOUR = 3
#         FIVE = 4
#         SIX = 5
#         SEVEN = 6
#         EIGHT = 7
#         NINE = 8
#
#     class CIRCLE(Enum):
#         ONE = 9
#         TWO = 10
#         THREE = 11
#         FOUR = 12
#         FIVE = 13
#         SIX = 14
#         SEVEN = 15
#         EIGHT = 16
#         NINE = 17
#
#     class WAN(Enum):
#         ONE = 18
#         TWO = 19
#         THREE = 20
#         FOUR = 21
#         FIVE = 22
#         SIX = 23
#         SEVEN = 24
#         EIGHT = 25
#         NINE = 26
#
#     class SPECIAL(Enum):
#         RED_DRAGON = 27
#         GREEN_DRAGON = 28
#         WHITE_DRAGON = 29
#         EAST = 30
#         SOUTH = 31
#         WEST = 32
#         NORTH = 33
#
#     @staticmethod
#     def same_type(a, b):
#         return type(a) == type(b)
#
#     @staticmethod
#     def int2enum(x):
#         if x < 9:
#             return TileType.BAMBOO(x)
#         elif x < 18:
#             return TileType.CIRCLE(x)
#         elif x < 27:
#             return TileType.WAN(x)
#         else:
#             return TileType.SPECIAL(x)


class Resource:
    fn2type = {
        'MJd1': TILE_TYPE.SPECIAL_RED_DRAGON,
        'MJd2': TILE_TYPE.SPECIAL_GREEN_DRAGON,
        'MJd3': TILE_TYPE.SPECIAL_WHITE_DRAGON,
        'MJf1': TILE_TYPE.SPECIAL_EAST,
        'MJf2': TILE_TYPE.SPECIAL_SOUTH,
        'MJf3': TILE_TYPE.SPECIAL_WEST,
        'MJf4': TILE_TYPE.SPECIAL_NORTH,
        'MJs1': TILE_TYPE.BAMBOO_ONE,
        'MJs2': TILE_TYPE.BAMBOO_TWO,
        'MJs3': TILE_TYPE.BAMBOO_THREE,
        'MJs4': TILE_TYPE.BAMBOO_FOUR,
        'MJs5': TILE_TYPE.BAMBOO_FIVE,
        'MJs6': TILE_TYPE.BAMBOO_SIX,
        'MJs7': TILE_TYPE.BAMBOO_SEVEN,
        'MJs8': TILE_TYPE.BAMBOO_EIGHT,
        'MJs9': TILE_TYPE.BAMBOO_NINE,
        'MJt1': TILE_TYPE.CIRCLE_ONE,
        'MJt2': TILE_TYPE.CIRCLE_TWO,
        'MJt3': TILE_TYPE.CIRCLE_THREE,
        'MJt4': TILE_TYPE.CIRCLE_FOUR,
        'MJt5': TILE_TYPE.CIRCLE_FIVE,
        'MJt6': TILE_TYPE.CIRCLE_SIX,
        'MJt7': TILE_TYPE.CIRCLE_SEVEN,
        'MJt8': TILE_TYPE.CIRCLE_EIGHT,
        'MJt9': TILE_TYPE.CIRCLE_NINE,
        'MJw1': TILE_TYPE.WAN_ONE,
        'MJw2': TILE_TYPE.WAN_TWO,
        'MJw3': TILE_TYPE.WAN_THREE,
        'MJw4': TILE_TYPE.WAN_FOUR,
        'MJw5': TILE_TYPE.WAN_FIVE,
        'MJw6': TILE_TYPE.WAN_SIX,
        'MJw7': TILE_TYPE.WAN_SEVEN,
        'MJw8': TILE_TYPE.WAN_EIGHT,
        'MJw9': TILE_TYPE.WAN_NINE,
    }

    def __init__(self):
        self.resources = dict()
        pass

    def load(self, src_dir):
        imgs = glob.glob(os.path.join(src_dir, '*.png'))
        for img in imgs:
            t = os.path.splitext(os.path.basename(img))[0]
            if t not in Resource.fn2type:
                self.resources['hidden'] = pygame.image.load(img)
                continue
            self.resources[Resource.fn2type[t]] = pygame.image.load(img)


if __name__ == '__main__':
    print(TILE_TYPE.CIRCLE(3))
    print(TILE_TYPE.CIRCLE_ONE.value * 90)
    # assert TileType.CIRCLE.ONE == TileType.CIRCLE.ONE
    # a = [TileType.CIRCLE.ONE, TileType.CIRCLE.ONE]
    # a.remove(TileType.CIRCLE.ONE)
    # print(a)
    # assert TileType.same_type(TileType.CIRCLE.ONE, TileType.CIRCLE.THREE)
    # print(type(TileType.CIRCLE.ONE))