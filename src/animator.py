import os
import src.global_vars as cst


class Animated:
    def __init__(self, animation, animation_speed=1):
        if type(animation) is str:
            self.animation = [
                cst.SPRITES[os.path.join(animation, i)]
                for i in sorted(os.listdir(animation))
                if not os.path.isdir(os.path.join(animation, i))
            ]
        else:
            self.animation = animation
        self.animation_speed = animation_speed
        self.animation_counter = 0
        self.current_frame = 0
        self.in_progress = False

    def animate(self):
        if self.in_progress:
            if self.animation_counter < self.animation_speed:
                self.animation_counter += 1
            else:
                self.current_frame += 1
                if self.current_frame >= len(self.animation):
                    self.current_frame = 0
                    self.in_progress = False
                self.animation_counter = 0
