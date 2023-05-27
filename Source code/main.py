import pygame, sys
from player import Player
import obstacle
from alien import Alien, Extra
from random import choice, randint
from laser import Laser
from buff import Buff


class Game:
    def __init__(self):
        player_sprite = Player((screen_width / 2 , screen_height), screen_width, screen_height, 5)
        self.player = pygame.sprite.GroupSingle(player_sprite)
        self.lives = 2
        self.extra_lives = 5
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
        self.buff_drop = randint(8000, 10000)

        
        self.laser_sound = pygame.mixer.Sound('laser.wav')
        self.laser_sound.set_volume(0.5)
        self.explosion_sound = pygame.mixer.Sound('explode.wav')
        self.explosion_sound.set_volume(0.4)

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
                    alien_sprite = Alien('alien_1',x,y)
                elif 1 <= row_index <= 2: 
                    alien_sprite = Alien('alien_2',x,y)
                else: 
                    alien_sprite = Alien('alien_3',x,y)

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
        if current_time - self.last_shot_time >= self.buff_drop:
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
                    laser.kill()
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
                        font = pygame.font.Font('font.otf', 40)
                        lose_surf = font.render('You lose', False, 'white')
                        lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                        screen.blit(lose_surf, lose_rect)
                        pygame.mixer.music.load("Lose_Tune.ogg")
                        pygame.mixer.music.play(-1)  
                        pygame.mixer.music.set_volume(0.6)
                        pygame.display.update()
                        pygame.time.delay(3850)
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
                        font = pygame.font.Font('font.otf', 40)
                        lose_surf = font.render('You lose', False, 'white')
                        lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                        screen.blit(lose_surf, lose_rect)
                        pygame.mixer.music.load("Lose_Tune.ogg")
                        pygame.mixer.music.play(-1)  
                        pygame.mixer.music.set_volume(0.6)
                        pygame.display.update()
                        pygame.time.delay(3850)
                        pygame.quit()
                        sys.exit()
        
        if self.aliens:
            for alien in self.aliens:
                pygame.sprite.spritecollide(alien, self.blocks, True)
                if pygame.sprite.spritecollide(alien, self.player, False):
                    font = pygame.font.Font('font.otf', 40)
                    lose_surf = font.render('You lose', False, 'white')
                    lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                    screen.blit(lose_surf, lose_rect)
                    pygame.mixer.music.load("Lose_Tune.ogg")
                    pygame.mixer.music.play(-1)  
                    pygame.mixer.music.set_volume(0.6)
                    pygame.display.update()
                    pygame.time.delay(3850)
                    pygame.quit()
                    sys.exit()

        if self.blocks:
            for block in self.blocks:
                if pygame.sprite.spritecollide(block, self.player, False):
                    font = pygame.font.Font('font.otf', 40)
                    lose_surf = font.render('You lose', False, 'white')
                    lose_rect = lose_surf.get_rect(center = (screen_width / 2, screen_height / 2))
                    screen.blit(lose_surf, lose_rect)
                    pygame.mixer.music.load("Lose_Tune.ogg")
                    pygame.mixer.music.play(-1)  
                    pygame.mixer.music.set_volume(0.6)
                    pygame.display.update()
                    pygame.time.delay(3850)
                    pygame.quit()
                    sys.exit()

        collided_buffs = pygame.sprite.spritecollide(self.player.sprite, self.buffs, True)
        for buff in collided_buffs:
            if buff.cek == 1:
                buff_sound = pygame.mixer.Sound('buff.wav')
                buff_sound.set_volume(0.4)
                self.player.sprite.laser_cooldown -= 150  
                self.player.sprite.laser_cooldown = max(100, self.player.sprite.laser_cooldown) 
                buff_sound.play()
            elif buff.cek == 2:
                buff_sound = pygame.mixer.Sound('extra_lives.wav')
                buff_sound.set_volume(0.6)
                self.gain_plus_life()
                buff_sound.play()
            elif buff.cek == 3:
                buff_sound = pygame.mixer.Sound('buff.wav')
                buff_sound.set_volume(0.4)
                self.player.sprite.multishot = True
                buff_sound.play()



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
            font = pygame.font.Font('font.otf', 40)
            victory_surf = font.render('You win', False, 'white')
            victory_rect = victory_surf.get_rect(center = (screen_width / 2, screen_height / 2))
            screen.blit(victory_surf, victory_rect)
            pygame.mixer.music.load("Victory_Tune.ogg")
            pygame.mixer.music.play(-1) 
            pygame.mixer.music.set_volume(0.6)
            pygame.display.update()
            pygame.time.delay(6500)
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

class BackgroundGame:
    def __init__ (self):
        self.bg = pygame.image.load('bg_game.png').convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (screen_width, screen_height))
        self.opacity = 200

    def draw(self):
        temp_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        temp_surface.blit(self.bg, (0, 0))
        temp_surface.set_alpha(self.opacity)
        screen.blit(temp_surface, (0, 0))


def show_menu():
    pygame.init()

    screen_width = 800
    screen_height = 600 
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Perang Bintang")  

    background_menu = pygame.image.load("bg_menu.jpg").convert()
    background_menu = pygame.transform.scale(background_menu, (screen_width, screen_height))

    pygame.mixer.music.load("Game_theme.ogg")
    pygame.mixer.music.play(-1)  
    pygame.mixer.music.set_volume(0.6)

    button_click_sound = pygame.mixer.Sound("tombol.wav")
    button_click_sound.set_volume(0.45)

    menu_selected = False

    all_sprites = pygame.sprite.Group()

    extra_sprite = Extra('left', screen_width)
    all_sprites.add(extra_sprite)

    while not menu_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    menu_selected = True
                    button_click_sound.play()
                elif exit_button_rect.collidepoint(mouse_pos):
                    button_click_sound.play()
                    pygame.quit()
                    sys.exit()

        all_sprites.update()
        screen.blit(background_menu, (0, 0))  
        all_sprites.draw(screen)

        font = pygame.font.Font('font.otf', 45)
        text = font.render("Perang bintang", True, (125, 255, 255))
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 150))
        screen.blit(text, text_rect)
        
        font = pygame.font.Font('font.otf', 30)
        start_button = pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 20, 150, 50)
        start_button_rect = pygame.draw.rect(screen, (0, 0, 0), start_button)
        start_text = font.render("Start", True, (255, 255, 255))
        start_text_rect = start_text.get_rect(center=start_button_rect.center)
        screen.blit(start_text, start_text_rect)

        exit_button = pygame.Rect(screen_width // 2 - 75, screen_height // 2 + 95, 150, 50)
        exit_button_rect = pygame.draw.rect(screen, (0, 0, 0), exit_button)
        exit_text = font.render("Exit", True, (255, 255, 255))
        exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
        screen.blit(exit_text, exit_text_rect)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    show_menu()

    pygame.init()
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    game = Game()
    background = BackgroundGame()
    pygame.mixer.music.set_volume(0.3)

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