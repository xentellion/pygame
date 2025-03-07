import json
import os
import src.global_vars as cst


@staticmethod
def get_weapons():
    with open("configs/weapons.json", "r", encoding="utf-8") as f:
        weapons = json.load(f)
        for k, v in weapons.items():
            cst.WEAPONS[k] = Weapon(**v)


class Weapon:
    def __init__(self, animation, damage, particles, animation_speed):
        self.animation = [
            cst.SPRITES[os.path.join(animation, i)]
            for i in sorted(os.listdir(animation))
            if not os.path.isdir(os.path.join(animation, i))
        ]
        self.particles = GunFlare(
            animation=[
                cst.SPRITES[os.path.join(particles, i)]
                for i in sorted(os.listdir(particles))
            ],
            animation_speed=animation_speed,
        )
        self.damage = damage
        self.is_shooting = False
        self.ammo = 100
        self.current_frame = 0
        self.animation_counter = 0
        self.animation_speed = animation_speed

    def shoot(self):
        if not self.is_shooting and self.ammo > 0:
            self.is_shooting = True
            self.ammo -= 1
            self.particles.is_playing = True

    def draw_gun(self):
        weapon_rect = self.animation[self.current_frame]
        weapon_pos = (
            cst.WIDTH // 2 - weapon_rect.get_width() // 2,
            cst.HEIGHT - weapon_rect.get_height(),
        )

        if self.is_shooting:
            if self.animation_counter < self.animation_speed:
                self.animation_counter += 1
            else:
                self.current_frame += 1
                if self.current_frame == len(self.animation):
                    self.current_frame = 0
                    self.is_shooting = False
                self.animation_counter = 0

        return (weapon_rect, weapon_pos)


class GunFlare:
    def __init__(self, animation, animation_speed):
        self.animation = animation
        self.current_frame = 0
        self.animation_counter = 0
        self.animation_speed = animation_speed  # From parent
        self.is_playing = False

    def draw_flare(self):
        if self.is_playing:
            flare_rect = self.animation[self.current_frame]

            if self.animation_counter < self.animation_speed:
                self.animation_counter += 1
            else:
                self.current_frame += 1
                if self.current_frame == len(self.animation):
                    self.current_frame = 0
                    self.is_playing = False
                self.animation_counter = 0

            return flare_rect
        return False
