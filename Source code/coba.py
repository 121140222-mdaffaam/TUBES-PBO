import pygame, sys
import obstacle
from random import choice, randint

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, x_constraint, y_constraint, speed):
        super().__init__()
        self.image = pygame.image.load('spaceship_1.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(midbottom = pos)
        self.speed = speed
        self.max_x_constraint = x_constraint
        self.max_y_constraint = y_constraint
        self.ready = True
        self.laser_time = 0
        self.laser_cooldown = 600

        self.lasers = pygame.sprite.Group()
        self.laser_sound = pygame.mixer.Sound('tod.mp3')
        self.laser_sound.set_volume(0.3)

        self.multishot = False  # Flag for multishot


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
            # Create multiple lasers
            laser1 = Laser(self.rect.center, -8, self.rect.bottom)
            laser2 = Laser((self.rect.left + 5, self.rect.centery), -7, self.rect.bottom)
            laser3 = Laser((self.rect.right - 5, self.rect.centery), -7, self.rect.bottom)
            self.lasers.add(laser1, laser2, laser3)
        else:
            # Create a single laser
            self.lasers.add(Laser(self.rect.center, -8, self.rect.bottom))

    def update(self):
        self.get_input()
        self.constraint()
        self.recharge()
        self.lasers.update()

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, screen_height):
        super().__init__()
        self.image = pygame.Surface((4,20))
        if speed != 10:
            self.image.fill('white')
        else:
            self.image.fill('red')
        self.rect = self.image.get_rect(center = pos)
        self.speed = speed
        self.height_y_constraint = screen_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_constraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()

class Alien(pygame.sprite.Sprite) :
        def __init__(self, color, x, y):
            super().__init__()
            file_path = color + '.jpg'
            self.image = pygame.image.load(file_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.rect = self.image.get_rect(topleft = (x,y))

            if color == 'red': self.value = 100
            elif color == 'green': self.value = 200
            else: self.value = 300

        def update(self, direction):
              self.rect.x += direction

class Extra(pygame.sprite.Sprite):
    def __init__(self, side, screen_width):
        super().__init__()
        self.image = pygame.image.load('spacemonkey.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (75, 75))
        if side == 'right':
            x = screen_width + 50
            self.speed = -1
        else:
            x = -50
            self.speed =  1

        self.rect = self.image.get_rect(topleft = (x, 50))

    def update(self):
        self.rect.x += self.speed

class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft = (x, y))

shape = [
'xx           xx',
 'xxx       xxx',
  'xxxxxxxxxxx',
  'xxxxxxxxxxx',
  'xxxx   xxxx',
   'xxxxxxxxx',
    'xxxxxxx']

class Buff(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
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
        if self.rect.top > screen_height:
            self.kill()

class Game:
    def __init__(self):
        player_sprite = Player((screen_width / 2 , screen_height), screen_width, screen_height, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        self.lives = 2
        self.extra_lives = 3
        self.plus_lives = 0
        self.live_surf = pygame.image.load('spaceship_1.png').convert_alpha()
        self.live_surf = pygame.transform.scale(self.live_surf, (35, 35))
        self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * (self.lives + self.plus_lives) + 20)
        self.score = 0
        self.font = pygame.font.Font('font.otf', 20)
        self.shape = obstacle.shape
        self.block_size = 6
        self.blocks = pygame.sprite.Group()
        self.obstacle_amount = 4
        self.obstacle_x_positions = [num * (screen_width / self.obstacle_amount) for num in range(self.obstacle_amount)]
        self.create_multiple_obstacles(*self.obstacle_x_positions, x_start = screen_width / 15, y_start = 450)
        self.aliens = pygame.sprite.Group()
        self.alien_lasers = pygame.sprite.Group()
        self.alien_setup(rows = 6, cols = 8)
        self.alien_direction = 1
        self.extra = pygame.sprite.GroupSingle()
        self.extra_laser = pygame.sprite.GroupSingle()
        self.extra_spawn_time = randint(600, 800)
        self.buffs = pygame.sprite.Group()
        self.last_shot_time = 0
        self.cooldown = randint(800, 1000)

        music = pygame.mixer.Sound('Monkeys Spinning Monkeys.mp3')
        music.set_volume(0.5)
        music.play(loops = -1)
        self.laser_sound = pygame.mixer.Sound('tod.mp3' )
        self.laser_sound.set_volume(0.2)
        self.explosion_sound = pygame.mixer.Sound('duar.mp3')
        self.explosion_sound.set_volume(0.2)

    def create_obstacle(self, x_start, y_start, offset_x):
        for row_index, row in enumerate(self.shape):
            for col_index, col in enumerate(row):
                if col == 'x':
                    x = x_start + col_index * self.block_size + offset_x
                    y = y_start + row_index * self.block_size
                    block = obstacle.Block(self.block_size, (0, 255, 255), x, y)
                    self.blocks.add(block)

    def create_multiple_obstacles(self,*offset ,x_start, y_start,):
        for offset_x in offset:
            self.create_obstacle(x_start, y_start, offset_x)

    def alien_setup(self, rows, cols, x_distance = 69, y_distance = 55, x_offset = 30, y_offset = 70):
        for row_index, row in enumerate(range(rows)):
            for col_index, col in enumerate(range(cols)):
                x = col_index * x_distance + x_offset
                y = row_index * y_distance + y_offset

                if row_index == 0: 
                    alien_sprite = Alien('blue',x,y)
                elif 1 <= row_index <= 2: 
                    alien_sprite = Alien('green',x,y)
                else: 
                    alien_sprite = Alien('red',x,y)

                self.aliens.add(alien_sprite)

    def alien_position_checker(self):
        all_aliens = self.aliens.sprites()
        for alien in all_aliens:
            if alien.rect.right >= screen_width:
                self.alien_direction = -1
                self.alien_move_down(1)
            elif alien.rect.left <= 0:
                self.alien_direction = 1
                self.alien_move_down(1)

    def alien_move_down(self,distance):
        if self.aliens:
            for alien in self.aliens.sprites():
                alien.rect.y += distance

    def alien_shoot(self):
        if self.aliens.sprites():
            random_alien = choice(self.aliens.sprites())
            laser_sprite = Laser(random_alien.rect.center, 6, screen_height)
            self.alien_lasers.add(laser_sprite)


    def extra_shoot(self):
        if self.extra.sprites():
            extra_sprite = self.extra.sprite
            extra_laser_sprite = Laser(extra_sprite.rect.center, 10, screen_height)
            self.extra_laser.add(extra_laser_sprite)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.cooldown:
            if self.extra.sprites():
                buff = Buff(extra_sprite.rect.center)
                self.buffs.add(buff)
                self.last_shot_time = current_time


    def extra_alien_timer(self):
        self.extra_spawn_time -= 1
        if self.extra_spawn_time <= 0 and self.extra_lives != 0:
            self.extra.add(Extra(choice(['right', 'left']),screen_width))
            self.extra_spawn_time = randint(1400, 1700)

    def gain_plus_life(self):
        self.plus_lives += 1

    def collision_check(self):
        total_lives = self.lives + self.plus_lives
        if self.player.sprite.lasers:
            for laser in self.player.sprite.lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                aliens_hit = pygame.sprite.spritecollide(laser,self.aliens, True)
                if aliens_hit:
                    for alien in aliens_hit:
                        self.score += alien.value
                    self.explosion_sound.play()
                if pygame.sprite.spritecollide(laser, self.extra, False):
                    laser.kill()
                    self.extra_lives -= 1
                    if self.extra_lives <= 0:
                        pygame.sprite.spritecollide(laser, self.extra, True)
                        self.score += 500
        
        if self.alien_lasers:
            for laser in self.alien_lasers:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 1
                    if total_lives <= 0:
                        lose_surf = self.font.render('You lose', False, 'white')
                        lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                        screen.blit(lose_surf, lose_rect)
                        pygame.display.update()
                        pygame.time.delay(3000)
                        pygame.quit()
                        sys.exit()
        
        if self.extra_laser:
            for laser in self.extra_laser:
                if pygame.sprite.spritecollide(laser, self.blocks, True):
                    laser.kill()
                if pygame.sprite.spritecollide(laser, self.player, False):
                    laser.kill()
                    self.lives -= 2
                    if total_lives <= 0:
                        lose_surf = self.font.render('You lose', False, 'white')
                        lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                        screen.blit(lose_surf, lose_rect)
                        pygame.display.update()
                        pygame.time.delay(3000)
                        pygame.quit()
                        sys.exit()
        
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    lose_surf = self.font.render('You lose', False, 'white')
                    lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                    screen.blit(lose_surf, lose_rect)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    pygame.quit()
                    sys.exit()

        if self.blocks:
            for block in self.blocks:
                if pygame.sprite.spritecollide(block, self.player, False):
                    lose_surf = self.font.render('You lose', False, 'white')
                    lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                    screen.blit(lose_surf, lose_rect)
                    pygame.display.update()
                    pygame.time.delay(3000)
                    pygame.quit()
                    sys.exit()

        collided_buffs = pygame.sprite.spritecollide(self.player.sprite, self.buffs, True)
        for buff in collided_buffs:
            if buff.cek == 1:
                self.player.sprite.laser_cooldown -= 150  # Reduce laser cooldown by 100
                self.player.sprite.laser_cooldown = max(100, self.player.sprite.laser_cooldown)  # Ensure non-negative value
            elif buff.cek == 2:
                self.gain_plus_life()
            elif buff.cek == 3:
                self.player.sprite.multishot = True



    def display_lives(self):
        total_lives = self.lives + self.plus_lives + 1
        for live in range(total_lives):
            self.live_x_start_pos = screen_width - (self.live_surf.get_size()[0] * total_lives + 30)
            x = self.live_x_start_pos + (live * (self.live_surf.get_size()[0] + 5))
            screen.blit(self.live_surf, (x, 8))
    
    def display_score(self):
        score_surf = self.font.render(f'score: {self.score}',False, 'white')
        score_rect = score_surf.get_rect(topleft = (10, 10))
        screen.blit(score_surf, score_rect)

    def victory_message(self):
        if not self.aliens.sprites() and not self.extra.sprites():
            victory_surf = self.font.render('You won', False, 'white')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)
            pygame.display.update()
            pygame.time.delay(3000)
            pygame.quit()
            sys.exit()

    def run(self):
        self.player.update()
        self.aliens.update(self.alien_direction)
        self.alien_position_checker()
        self.alien_lasers.update()
        self.extra_alien_timer()
        self.extra_laser.draw(screen)
        self.extra_laser.update()
        self.extra.update()
        self.collision_check()
        self.player.sprite.lasers.draw(screen)
        self.player.draw(screen)
        self.blocks.draw(screen)
        self.aliens.draw(screen)
        self.alien_lasers.draw(screen)
        self.extra.draw(screen)
        self.display_lives()
        self.display_score()
        self.victory_message()
        self.buffs.update()
        self.buffs.draw(screen)

class Background:
    def __init__ (self):
        self.bg = pygame.image.load('103717879_p0_master1200.jpg').convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (screen_width, screen_height))
        self.opacity = 200

    def draw(self):
        temp_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        temp_surface.blit(self.bg, (0, 0))
        temp_surface.set_alpha(self.opacity)
        screen.blit(temp_surface, (0, 0))

if __name__ == '__main__':
    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    background = Background()

    ALIENLASER = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIENLASER, 800)

    EXTRALASER = pygame.USEREVENT + 2
    pygame.time.set_timer(EXTRALASER, 800)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == ALIENLASER:
                game.alien_shoot()
            if event.type == EXTRALASER:
                game.extra_shoot()

        game.buffs.update()
        screen.fill((30, 30, 30))
        background.draw()
        game.run()

        pygame.display.flip()
        clock.tick(60)
