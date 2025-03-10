import json
import src.global_vars as cst
from src.animator import Animated
from pygame import mixer


@staticmethod
def get_weapons():
    with open("configs/weapons.json", "r", encoding="utf-8") as f:
        weapons = json.load(f)
        for k, v in weapons.items():
            cst.WEAPONS[k] = Weapon(**v)


class Weapon(Animated):
    def __init__(self, animation, damage, particles, animation_speed, sound):
        super().__init__(animation)
        self.particles = GunFlare(
            animation=particles,
            animation_speed=animation_speed,
        )
        self.damage = damage
        self.ammo = 100
        self.dealing_damage = False
        self.sound = mixer.Sound(sound)

    def shoot(self):
        if not self.in_progress and self.ammo > 0:
            self.in_progress = True
            self.ammo -= 1
            self.particles.in_progress = True
            self.dealing_damage = True
            self.sound.play()

    def draw_gun(self):
        weapon_rect = self.animation[self.current_frame]
        weapon_pos = (
            cst.WIDTH // 2 - weapon_rect.get_width() // 2,
            cst.HEIGHT - weapon_rect.get_height(),
        )
        self.animate()

        return (weapon_rect, weapon_pos)


class GunFlare(Animated):
    def __init__(self, animation, animation_speed):
        super().__init__(animation)

    def draw_flare(self):
        if self.in_progress:
            flare_rect = self.animation[self.current_frame]
            self.animate()
            return flare_rect
        return False
