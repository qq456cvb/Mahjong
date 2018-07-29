import pygame


class Tile(pygame.sprite.Sprite):
    def __init__(self, image, type):
        pygame.sprite.Sprite.__init__(self)

        self.image = image
        self._type = type
        self.rect = self.image.get_rect()


class HandTile(Tile):
    def __init__(self, image, type):
        Tile.__init__(self, image, type)


class Button(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def on_click(self):
        pass


class Text(pygame.sprite.Sprite):
    pygame.font.init()
    font = pygame.font.SysFont('wenquanyimicroheimono', 30)

    def __init__(self, text, pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = Text.font.render(text, True, (0, 204, 102))
        # self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]
