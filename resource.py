import glob
import os
import pygame
from enum import Enum


class TileType:

    class BAMBOO(Enum):
        ONE = 0
        TWO = 1
        THREE = 2
        FOUR = 3
        FIVE = 4
        SIX = 5
        SEVEN = 6
        EIGHT = 7
        NINE = 8

    class CIRCLE(Enum):
        ONE = 9
        TWO = 10
        THREE = 11
        FOUR = 12
        FIVE = 13
        SIX = 14
        SEVEN = 15
        EIGHT = 16
        NINE = 17

    class WAN(Enum):
        ONE = 18
        TWO = 19
        THREE = 20
        FOUR = 21
        FIVE = 22
        SIX = 23
        SEVEN = 24
        EIGHT = 25
        NINE = 26

    class SPECIAL(Enum):
        RED_DRAGON = 27
        GREEN_DRAGON = 28
        WHITE_DRAGON = 29
        EAST = 30
        SOUTH = 31
        WEST = 32
        NORTH = 33

    @staticmethod
    def same_type(a, b):
        return type(a) == type(b)

    @staticmethod
    def int2enum(x):
        if x < 9:
            return TileType.BAMBOO(x)
        elif x < 18:
            return TileType.CIRCLE(x)
        elif x < 27:
            return TileType.WAN(x)
        else:
            return TileType.SPECIAL(x)


class Resource:
    fn2type = {
        'MJd1': TileType.SPECIAL.RED_DRAGON,
        'MJd2': TileType.SPECIAL.GREEN_DRAGON,
        'MJd3': TileType.SPECIAL.WHITE_DRAGON,
        'MJf1': TileType.SPECIAL.EAST,
        'MJf2': TileType.SPECIAL.SOUTH,
        'MJf3': TileType.SPECIAL.WEST,
        'MJf4': TileType.SPECIAL.NORTH,
        'MJs1': TileType.BAMBOO.ONE,
        'MJs2': TileType.BAMBOO.TWO,
        'MJs3': TileType.BAMBOO.THREE,
        'MJs4': TileType.BAMBOO.FOUR,
        'MJs5': TileType.BAMBOO.FIVE,
        'MJs6': TileType.BAMBOO.SIX,
        'MJs7': TileType.BAMBOO.SEVEN,
        'MJs8': TileType.BAMBOO.EIGHT,
        'MJs9': TileType.BAMBOO.NINE,
        'MJt1': TileType.CIRCLE.ONE,
        'MJt2': TileType.CIRCLE.TWO,
        'MJt3': TileType.CIRCLE.THREE,
        'MJt4': TileType.CIRCLE.FOUR,
        'MJt5': TileType.CIRCLE.FIVE,
        'MJt6': TileType.CIRCLE.SIX,
        'MJt7': TileType.CIRCLE.SEVEN,
        'MJt8': TileType.CIRCLE.EIGHT,
        'MJt9': TileType.CIRCLE.NINE,
        'MJw1': TileType.WAN.ONE,
        'MJw2': TileType.WAN.TWO,
        'MJw3': TileType.WAN.THREE,
        'MJw4': TileType.WAN.FOUR,
        'MJw5': TileType.WAN.FIVE,
        'MJw6': TileType.WAN.SIX,
        'MJw7': TileType.WAN.SEVEN,
        'MJw8': TileType.WAN.EIGHT,
        'MJw9': TileType.WAN.NINE,
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
    print(TileType.CIRCLE(3))
    print(TileType.CIRCLE.ONE.value * 90)
    # assert TileType.CIRCLE.ONE == TileType.CIRCLE.ONE
    # a = [TileType.CIRCLE.ONE, TileType.CIRCLE.ONE]
    # a.remove(TileType.CIRCLE.ONE)
    # print(a)
    # assert TileType.same_type(TileType.CIRCLE.ONE, TileType.CIRCLE.THREE)
    # print(type(TileType.CIRCLE.ONE))