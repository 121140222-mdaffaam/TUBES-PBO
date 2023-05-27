import pygame

class Alien(pygame.sprite.Sprite) :
        def __init__(self, type, x, y):
            super().__init__()
            file_path = type + '.jpg'
            self.image = pygame.image.load(file_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect = self.image.get_rect(topleft = (x,y))

            if type == 'alien_3': self.value = 100
            elif type == 'alien_2': self.value = 200
            else: self.value = 300

        def update(self, direction):
              self.rect.x += direction

class Extra(pygame.sprite.Sprite):
    def __init__(self, side, screen_width):
        super().__init__()
        self.image = pygame.image.load('extra_spacemonkey.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 75))
        if side == 'right':
            x = screen_width + 50
            self.speed = -1
        else:
            x = -50
            self.speed =  1

        self.rect = self.image.get_rect(topleft = (x, 25))

    def update(self):
        self.rect.x += self.speed
