import pygame
from random import choice

class Buff(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.screen_height = 800
        random = choice([1, 2, 3])
        if random == 1:
            self.jenis = 'rapidshot'
            self.cek = 1
        elif random == 2:
            self.jenis = 'spaceship_1'
            self.cek = 2
        elif random == 3:
            self.jenis = 'multishot'
            self.cek = 3
        file_path = self.jenis + '.png'
        self.image = pygame.image.load(file_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (40, 40))
        self.rect = self.image.get_rect(center=pos)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > self.screen_height:
            self.kill()