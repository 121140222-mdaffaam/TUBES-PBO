import pygame
from laser import Laser
from buff import Buff

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, x_constraint, y_constraint, speed):
        super().__init__()
        self.image = pygame.image.load('spaceship.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.max_x_constraint = x_constraint
        self.max_y_constraint = y_constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600

        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('laser.wav')
        self.laser_sound.set_volume(0.6)

        self.multishot = False

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        elif keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_SPACE] and self.ready:
            self.shoot_laser()
            self.ready = False
            self.laser_time = pygame.time.get_ticks()
            self.laser_sound.play()

    def recharge(self):
        if not self.ready:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_time >= self.laser_cooldown:
                self.ready = True

    def constraint(self):
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= self.max_x_constraint:
            self.rect.right = self.max_x_constraint
        if self.rect.bottom >= self.max_y_constraint:
            self.rect.bottom = self.max_y_constraint
        if self.rect.top <= 0:
            self.rect.top = 0

    def shoot_laser(self):
        if self.multishot:
            self.laser_sound = pygame.mixer.Sound('Multishot.wav')
            self.laser_sound.set_volume(0.8)
            laser1 = Laser(self.rect.center, -8, self.rect.bottom)
            laser2 = Laser((self.rect.left + 5, self.rect.centery), -7, self.rect.bottom)
            laser3 = Laser((self.rect.right - 5, self.rect.centery), -7, self.rect.bottom)
            self.lasers.add(laser1, laser2, laser3)
        else:
            self.lasers.add(Laser(self.rect.center, -8, self.rect.bottom))

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()