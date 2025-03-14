import src.global_vars as cst
from src.animator import Animated
from pygame import mixer
from src.interaction import raycast_interact


# I made it possible to use multiple weapons but made only one
# Genius
class Weapon(Animated):
    def __init__(self, animation, damage, particles, animation_speed, sound):
        super().__init__(animation)
        self.particles = GunFlare(
            animation=particles,
            animation_speed=animation_speed,
        )
        self.damage = damage
        self.ammo = 10
        self.dealing_damage = False  # Is used to deal damage on a single frame
        self.sound = mixer.Sound(sound)  # No reload so its fine

    def shoot(self, target):
        if not self.in_progress and self.ammo > 0:
            self.in_progress = True
            self.particles.in_progress = True
            self.ammo -= 1
            self.dealing_damage = True
            self.sound.play()
            if target[-1][-1].hp and raycast_interact(target[-1][-1].position):
                target[-1][-1].take_damage(cst.PLAYER.current_weapon.damage)
                cst.PLAYER.current_weapon.dealing_damage = False

    def render_gun(self):
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
        # I honestly should adjust it for multiple flares at once
        # But the animation is slower than reload so who cares
        if self.in_progress:
            flare_rect = self.animation[self.current_frame]
            self.animate()
            return flare_rect
        return False
