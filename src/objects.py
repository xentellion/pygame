from math import sqrt, atan2, cos, pi, inf
import os
import pygame
import src.global_vars as cst
from src.animator import Animated
from src.interaction import raycast_interact


class Objects:
    def __init__(self):
        # Might replace with image separation with PIL
        # To keep everything in a single sprite atlas
        for subdir, dirs, files in os.walk("sprites"):
            for file in files:
                path = os.path.join(subdir, file)
                cst.SPRITES[path] = pygame.image.load(path).convert_alpha()
        self.obj_list = []

    def hit_sprite(self):
        return min(
            [(x.is_aimed_at(), x) for x in self.obj_list],
            key=lambda x: x[0],
            default=(inf, 0),
        )


class GameObject(Animated):

    def __init__(
        self,
        position: tuple,
        name: str,
        default: str,
        animations: dict,
        shift: float,
        scale: float,
        animation_dist: int,
        animation_speed: int,
        transparent: bool,
        hp: int,
        npc: bool,
        damage_sound: str,
        death_sound: str,
        damage: int = 1,
    ):
        super().__init__(
            None,
            animation_speed=animation_speed,
        )
        # Once again, junk made for feature not implemented
        # This time - for multiple animations on npc
        # Bruh
        if animations:
            self.animations = {
                k: [cst.SPRITES[os.path.join(v, i)] for i in os.listdir(v)]
                for k, v in animations.items()
            }
            self.animation = self.animations["idle"]
        else:
            self.animations = self.animation = animations

        self.position = tuple(map(lambda x: x * cst.TILE, position))
        self.name = name
        self.default = cst.SPRITES[default]

        self.shift = shift
        self.scale = scale
        self.animation_dist = animation_dist

        self.current_sprite = self.default
        self.transparent = transparent

        # Might be breakable or unbreakable object, not just an enemy
        self.hp = hp
        self.current_hp = hp

        self.damage = damage

        self.damage_sound = (
            pygame.mixer.Sound(damage_sound) if damage_sound else damage_sound
        )
        self.death_sound = (
            pygame.mixer.Sound(death_sound) if death_sound else death_sound
        )

        self.npc = npc

    def is_aimed_at(self):
        if (
            cst.CENTRAL_RAY - cst.TEXTURE_SIDE // 2
            < self.extra_ray  # Sketchy, WILL crash if face_player never called
            < cst.CENTRAL_RAY + 3 * cst.TEXTURE_SIDE // 2
            and not self.transparent
        ):
            return (self.distance, self.proj_height)
        return inf, 0

    def face_player(self):
        dx = self.position[0] - cst.PLAYER.pos[0]
        dy = self.position[1] - cst.PLAYER.pos[1]
        self.distance = sqrt(dx**2 + dy**2)

        self.theta = atan2(dy, dx)
        gamma = self.theta - cst.PLAYER.angle
        # flip the sprite to keep it bein seen
        if dx > 0 and pi <= cst.PLAYER.angle <= 2 * pi or dx < 0 and dy < 0:
            gamma += cst.DOUBLE_PI

        sprite_shift = int(gamma / cst.RAY_DELTA)
        middle_ray = cst.CENTRAL_RAY + sprite_shift
        self.distance *= cos(cst.HALV_FOV - middle_ray * cst.RAY_DELTA)
        self.distance = max(
            self.distance, cst.EPSILON
        )  # to keep it from losing ALL frames up close

        self.extra_ray = middle_ray + cst.EXTRA_RAYS

        if 0 <= self.extra_ray <= cst.LAST_EXTRA_RAY and self.distance < cst.MAX_DIST:
            self.proj_height = min(  # Another frame sink
                int(cst.PROJ_COEFF / self.distance * self.scale), 2 * cst.HEIGHT
            )
            half_height = self.proj_height // 2
            vertical_shift = half_height * self.shift

            if self.animations and self.distance < self.animation_dist:
                self.in_progress = True  # To keep constant loop
                self.animate()
                self.current_sprite = self.animation[self.current_frame]

            sprite_position = (
                middle_ray * cst.SCALE - half_height,
                cst.HALF_HEIGHT - half_height + vertical_shift,
            )
            sprite = pygame.transform.scale(
                self.current_sprite, (self.proj_height, self.proj_height)
            )
            return (self.distance, sprite, sprite_position, None)
        else:
            return (False,)

    def move(self):
        # Just move hostile npc towards player if it is visible
        # Because i am NOT making proper pathfinding here
        # No, thank you!
        if raycast_interact(self.position):
            delta = (
                self.position[0] - cst.PLAYER.pos[0],
                self.position[1] - cst.PLAYER.pos[1],
            )
            dist = sqrt(sum(map(lambda x: x**2, delta)))
            if dist > cst.TILE:
                # play melee animation (NO ANIMATION)
                self.position = tuple(
                    map(lambda x, y: x + 1 if y < 0 else x - 1, self.position, delta)
                )
            # Aura damage
            # Those pesky fairies are dealing moral damage
            # by abusing your precious sunflowers
            if dist <= 1.5 * cst.TILE:
                cst.PLAYER.damage(self.damage)

    def take_damage(self, damage):
        if self.hp > 0:
            self.current_hp -= damage
            # animation, perchance?
            self.damage_sound.play(0)
            if self.current_hp <= 0:
                self.death()

    def death(self):
        print(f"{self.name} is slain!")
        # Insert animation (I don't have one)
        self.death_sound.play(0)
        cst.OBJECTS.obj_list.remove(self)
