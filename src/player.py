from math import sqrt, atan, sin, cos, copysign
import pygame
from operator import add
import src.global_vars as cst


class Player:
    def __init__(self, position):
        self.hp = 100
        self.max_hp = 100
        self.lives = 3
        # I made this list to hold all weapons in inventory but never made more than one
        # I blame sprites
        self.weaponry = []
        self.current_weapon = cst.WEAPONS[next(iter(cst.WEAPONS))]

        self.speed = cst.TILE // 16

        self.pos = position
        self.mouse_position = pygame.mouse.get_pos()
        self.sensitivity = 1440
        self.collider_side = cst.TILE // 4
        self.rect = pygame.Rect(*self.pos, self.collider_side, self.collider_side)
        self.angle = 0

        self.graze_sound = pygame.mixer.Sound("audio/graze.wav")
        self.death_sound = pygame.mixer.Sound("audio/pichuun.mp3")

    # Sticks to the walls and there is a chance to get stuck in a corner
    # Works, though
    def check_collision(self, dx, dy):
        if dx != 0:
            delta = self.collider_side // 2 * copysign(1, dx)
            x_check = (self.pos[0] + dx + delta, self.pos[1])
            x_in_1 = cst.mapping(x_check[0], x_check[1] + delta) in cst.GAME_MAP
            x_in_2 = cst.mapping(x_check[0], x_check[1] - delta) in cst.GAME_MAP
            if x_in_1 or x_in_2:
                dx = 0
        if dy != 0:
            delta = self.collider_side // 2 * copysign(1, dy)
            y_check = (self.pos[0], self.pos[1] + dy + delta)
            y_in_1 = cst.mapping(y_check[0] + delta, y_check[1]) in cst.GAME_MAP
            y_in_2 = cst.mapping(y_check[0] - delta, y_check[1]) in cst.GAME_MAP
            if y_in_1 or y_in_2:
                dy = 0
        return dx, dy

    def move(self, clock, keys):
        sin_a, cos_a = sin(self.angle), cos(self.angle)
        x_pos, y_pos = 0, 0

        if keys[pygame.K_w]:
            x_pos += cos_a
            y_pos += sin_a
        if keys[pygame.K_s]:
            x_pos -= cos_a
            y_pos -= sin_a
        if keys[pygame.K_a]:
            x_pos += sin_a
            y_pos -= cos_a
        if keys[pygame.K_d]:
            x_pos -= sin_a
            y_pos += cos_a

        x_pos, y_pos = self.check_collision(x_pos, y_pos)
        # Normalize if several inputs
        # No speedy diagonal movement, bucko
        length = sqrt(x_pos**2 + y_pos**2)
        if length > cst.EPSILON:
            self.pos = tuple(
                map(
                    add,
                    self.pos,
                    tuple(map(lambda x: x / length * self.speed, (x_pos, y_pos))),
                )
            )
        self.rect.center = self.pos[0], self.pos[1]

    def rotate(self, event):
        # MAN it is so uncomfortable
        if pygame.mouse.get_focused():
            difference = pygame.mouse.get_pos()[0] - cst.WIDTH // 2
            pygame.mouse.set_pos((cst.WIDTH // 2, cst.HALF_HEIGHT))
            self.angle += difference / self.sensitivity
            self.angle %= cst.DOUBLE_PI

    def shoot(self, event, target):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_weapon.shoot(target)

    def use(self, event):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            print("use")

    def damage(self, amount):
        if amount < 10:
            self.graze_sound.play()
        else:
            pass
            # grunt or something
        self.hp -= amount
        if self.hp <= 0:
            self.death()

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def give_ammo(self, amount):
        self.current_weapon.ammo += amount

    def death(self):
        self.lives -= 1
        self.death_sound.play(0)
        cst.GAME_OVER = True

    def restart(self, position):
        self.current_weapon.ammo = 10
        self.hp = self.max_hp
        self.pos = position
        self.angle = 0

    def quit(self, event):
        match event.type:
            case pygame.QUIT:
                return False
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
