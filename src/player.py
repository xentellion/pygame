from math import sqrt, atan, sin, cos, copysign
import pygame
from operator import add
import src.global_vars as cst


class Player:
    def __init__(self, position):
        self.hp = 100
        self.max_hp = 100

        self.weaponry = []
        self.current_weapon = cst.WEAPONS[next(iter(cst.WEAPONS))]

        self.speed = cst.TILE // 16

        self.pos = position
        self.mouse_position = pygame.mouse.get_pos()
        self.sensitivity = 90
        self.collider_radius = cst.TILE // 4
        self.rect = pygame.Rect(*self.pos, self.collider_radius, self.collider_radius)
        self.angle = 0

    def mapping(self, a, b):
        return (
            (a // cst.TILE) * cst.TILE,
            (b // cst.TILE) * cst.TILE,
        )

    # A bit sticky to the walls, but it works
    def check_collision(self, dx, dy, colliders):
        if dx != 0:
            delta = self.collider_radius // 2 * copysign(1, dx)
            if (
                self.mapping(self.pos[0] + dx + delta, self.pos[1] + delta) in colliders
            ) or (
                self.mapping(self.pos[0] + dx + delta, self.pos[1] - delta) in colliders
            ):
                dx = 0
        if dy != 0:
            delta = self.collider_radius // 2 * copysign(1, dy)
            if (
                self.mapping(self.pos[0] + delta, self.pos[1] + dy + delta) in colliders
            ) or (
                self.mapping(self.pos[0] - delta, self.pos[1] + dy + delta) in colliders
            ):
                dy = 0
        return dx, dy

    def move(self, clock, keys, colliders):
        # Imagine Wolfenstein 3d
        # but with STRAFE
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

        x_pos, y_pos = self.check_collision(x_pos, y_pos, colliders)
        # Normalize if several inputs
        ln = sqrt(x_pos**2 + y_pos**2)
        if ln > 1e-5:
            self.pos = tuple(
                map(
                    add,
                    self.pos,
                    tuple(map(lambda x: x / ln * self.speed, (x_pos, y_pos))),
                )
            )
        self.rect.center = self.pos[0], self.pos[1]

    def rotate(self, event):
        if event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            self.angle += atan(
                (pos[0] - self.mouse_position[0]) / self.sensitivity,
            )
            self.mouse_position = pos
            self.angle %= cst.DOUBLE_PI

    def quit(self, event):
        match event.type:
            case pygame.QUIT:
                return False
            case pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def shoot(self, event):
        if event.type == pygame.MOUSEBUTTONUP:
            self.current_weapon.shoot()

    def use(self, event):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            print("use")

    def damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.die()

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def die(self):
        pass
