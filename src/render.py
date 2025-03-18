from math import sin, cos
import os
import pygame
import src.global_vars as cst


class Render:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Liberation Serif", 30)
        self.textures = {}
        for subdir, dirs, files in os.walk("textures"):
            for file in files:
                path = os.path.join(subdir, file).replace(os.sep, "/")
                self.textures[path] = pygame.image.load(path).convert_alpha()

    def render_background(self):
        self.screen.fill(cst.CEILING_COLOR)  # "Sky"
        pygame.draw.rect(  # "Ground"
            self.screen,
            cst.FLOOR_COLOR,
            (
                0,
                cst.HEIGHT / 2,
                cst.WIDTH,
                cst.HEIGHT,
            ),
        )

    def render_walls(self):
        walls = []
        ox, oy = cst.PLAYER.pos
        # Bresenham's Line Algorythm
        # Because screw checking for a wall every meter of space
        xl, yl = cst.mapping(ox, oy)
        current_angle = cst.PLAYER.angle - cst.HALV_FOV

        # Fix empty texture crash
        default_texture = next(iter(self.textures))
        texture_v, texture_h = default_texture, default_texture

        for ray in range(cst.RAY_COUNT):
            # adjust trigonometry for possible 0 division
            if not (sin_a := sin(current_angle)):
                sin_a = cst.EPSILON
            if not (cos_a := cos(current_angle)):
                cos_a = cst.EPSILON

            # vertical steps
            x, dx = (xl + cst.TILE, 1) if cos_a >= 0 else (xl, -1)
            for _ in range(0, cst.WIDTH * 2, cst.TILE):
                depth_vert = (x - ox) / cos_a
                y_vert = oy + depth_vert * sin_a
                # Set texture based on hit point
                if (tile_v := cst.mapping(x + dx, y_vert)) in cst.GAME_MAP:
                    texture_v = cst.GAME_MAP[tile_v]
                    break
                x += dx * cst.TILE
            # Horizontal
            y, dy = (yl + cst.TILE, 1) if sin_a >= 0 else (yl, -1)
            for _ in range(0, cst.HEIGHT * 8, cst.TILE):
                depth_height = (y - oy) / sin_a
                x_horiz = ox + depth_height * cos_a
                if (tile_h := cst.mapping(x_horiz, y + dy)) in cst.GAME_MAP:
                    texture_h = cst.GAME_MAP[tile_h]
                    break
                y += dy * cst.TILE
            # depth projection
            depth, offset, texture = (
                (depth_vert, y_vert, texture_v)
                if depth_vert < depth_height
                else (depth_height, x_horiz, texture_h)
            )
            offset = int(offset) % cst.TILE
            depth *= cos(cst.PLAYER.angle - current_angle)
            depth = max(depth, cst.EPSILON)
            proj_height = int(cst.PROJ_COEFF / depth)
            # Depth shadow color (because fog is more silent hill's shtick)
            color = 255 - int(255 / (1 + depth**2 * cst.EPSILON))
            # prevent out-of-screen render for performance reasons
            if proj_height > cst.HEIGHT:
                texture_height = cst.TEXTURE_SIDE * cst.HEIGHT / proj_height
                # Dark shade for "depth"
                texture_slice = self.textures[texture].subsurface(
                    (
                        offset * cst.TEXTURE_SCALE,
                        cst.TEXTURE_SIDE // 2 - texture_height // 2,
                        cst.TEXTURE_SCALE,
                        texture_height,
                    )
                )
                texture_slice = pygame.transform.scale(
                    texture_slice, (cst.SCALE, cst.HEIGHT)
                )
                wall_position = (ray * cst.SCALE, 0)
            else:
                texture_slice = self.textures[texture].subsurface(
                    (
                        offset * cst.TEXTURE_SCALE,
                        0,
                        cst.TEXTURE_SCALE,
                        cst.TEXTURE_SIDE,
                    )
                )
                texture_slice = pygame.transform.scale(
                    texture_slice, (cst.SCALE, proj_height)
                )
                wall_position = (
                    ray * cst.SCALE,
                    cst.HALF_HEIGHT - proj_height // 2,
                )
            texture_slice.fill(
                pygame.Color(color, color, color, 0),
                special_flags=pygame.BLEND_RGBA_SUB,
            )

            current_angle += cst.RAY_DELTA
            walls.append((depth, texture_slice, wall_position, proj_height))
        aiming_point = (
            walls[cst.CENTRAL_RAY + cst.EXTRA_RAYS][0],
            walls[cst.CENTRAL_RAY + cst.EXTRA_RAYS][3],
        )
        return walls, aiming_point

    def render_world(self, elements):
        # Sort by Z axis (depth)
        for element in sorted(elements, key=lambda x: x[0], reverse=True):
            if element[0]:
                _, item, item_pos, _ = element
                self.screen.blit(item, item_pos)

    def render_gun(self, target):
        self.screen.blit(*cst.PLAYER.current_weapon.render_gun())
        # Draw flare if gun has fired
        if cst.PLAYER.current_weapon.in_progress:
            self.render_flare(target[:-1])

    def render_flare(self, target):
        self.shot_proj = min(target, key=lambda x: x[1])[1] // 2
        shot = cst.PLAYER.current_weapon.particles.draw_flare()
        if shot:
            shot = pygame.transform.scale(shot, (self.shot_proj, self.shot_proj))
            rect = shot.get_rect()
            self.screen.blit(
                shot,
                (cst.WIDTH // 2 - rect.w // 2, cst.HALF_HEIGHT - rect.h // 2),
            )
            del shot

    def render_ui(self):
        # Lives
        lives = f"Жизни: {cst.PLAYER.lives}"
        image = self.font.render(
            lives, 0, cst.TEXT_COLOR if cst.PLAYER.lives > 1 else cst.RED_COLOR
        )
        x, y = image.get_size()
        self.screen.blit(image, (cst.WIDTH - 65 - x, cst.HEIGHT - 90 - y))
        # HP
        hp = f"Здоровье: {cst.PLAYER.hp}/{cst.PLAYER.max_hp}"
        image = self.font.render(
            hp, 0, cst.TEXT_COLOR if cst.PLAYER.hp > 20 else cst.RED_COLOR
        )
        x, y = image.get_size()
        self.screen.blit(image, (cst.WIDTH - 65 - x, cst.HEIGHT - 50 - y))
        # Ammo
        num = cst.PLAYER.current_weapon.ammo
        ammo = f"Патроны: {num}"
        image = self.font.render(ammo, 0, cst.TEXT_COLOR if num else cst.RED_COLOR)
        x, y = image.get_size()
        self.screen.blit(image, (cst.WIDTH - 65 - x, cst.HEIGHT - 10 - y))

    def frame_count(self, clock):
        text = str(int(clock.get_fps()))
        image = self.font.render(text, 0, cst.TEXT_COLOR)
        self.screen.blit(image, (65, 10))

    def door_open(self):
        text = "Феи истреблены"
        image = self.font.render(text, 0, cst.TEXT_COLOR)
        self.screen.blit(image, (cst.WIDTH - 265, 10))

    def ui_screen(self, clock, text):
        # This method render splash screen with text
        # Used for win/lose and starting text
        # font = pygame.font.Font("fonts/amazdoomright2.ttf", 50)
        font = pygame.font.SysFont("LiberationSerif.ttf", 50)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        quit()
                    if cst.GAME_OVER is None:
                        return

            space = 1.5
            self.screen.fill(cst.CEILING_COLOR)
            temp_img = font.render(text[0], 0, cst.TEXT_COLOR)
            row_height = int(temp_img.get_height() * space)
            start_point = cst.HALF_HEIGHT - row_height * len(text) // 2
            height_shift = row_height - 1
            del temp_img, row_height

            for idx, strin in enumerate(text):
                image = font.render(strin, 0, cst.TEXT_COLOR)
                width, height = image.get_size()
                width_shift = cst.WIDTH // 2 - width // 2
                self.screen.blit(
                    image,
                    (
                        width_shift,
                        start_point + height_shift * idx,
                        height,
                        width,
                    ),
                )
            pygame.display.flip()
            clock.tick(cst.FPS_LOCK)
