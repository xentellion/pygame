from math import sin, cos
import os
import pygame
import src.global_vars as cst
from src.player import Player
from src.interaction import raycast_interact


class Render:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Liberation Serif", 30)
        self.textures = {}
        for subdir, dirs, files in os.walk("textures"):
            for file in files:
                path = os.path.join(subdir, file)
                self.textures[path] = pygame.image.load(path).convert_alpha()

    def render_background(self, player):
        self.screen.fill(cst.CEILING_COLOR)
        pygame.draw.rect(
            self.screen,
            cst.FLOOR_COLOR,
            (
                0,
                cst.HEIGHT / 2,
                cst.WIDTH,
                cst.HEIGHT,
            ),
        )

    def render_walls(self, player: Player, level_map):
        walls = []
        ox, oy = player.pos
        xl, yl = cst.mapping(ox, oy)
        current_angle = player.angle - cst.HALV_FOV

        # Fix empty texture crash
        default_texture = next(iter(self.textures))
        texture_v, texture_h = default_texture, default_texture
        del default_texture

        for ray in range(cst.RAY_COUNT):
            # adjust for possible 0 division
            if not (sin_a := sin(current_angle)):
                sin_a = cst.EPSILON
            if not (cos_a := cos(current_angle)):
                cos_a = cst.EPSILON

            # vertical
            x, dx = (xl + cst.TILE, 1) if cos_a >= 0 else (xl, -1)
            for _ in range(0, cst.WIDTH * 2, cst.TILE):
                depth_vert = (x - ox) / cos_a
                yv = oy + depth_vert * sin_a
                # Set texture based on hit point
                if (tile_v := cst.mapping(x + dx, yv)) in level_map:
                    texture_v = level_map[tile_v]
                    break
                x += dx * cst.TILE
            # Horizontal
            y, dy = (yl + cst.TILE, 1) if sin_a >= 0 else (yl, -1)
            for _ in range(0, cst.HEIGHT * 8, cst.TILE):
                depth_height = (y - oy) / sin_a
                xh = ox + depth_height * cos_a
                if (tile_h := cst.mapping(xh, y + dy)) in level_map:
                    texture_h = level_map[tile_h]
                    break
                y += dy * cst.TILE
            # depth projection
            depth, offset, texture = (
                (depth_vert, yv, texture_v)
                if depth_vert < depth_height
                else (depth_height, xh, texture_h)
            )
            offset = int(offset) % cst.TILE
            depth *= cos(player.angle - current_angle)
            depth = max(depth, cst.EPSILON)
            proj_height = int(cst.PROJ_COEFF / depth)

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
                wall_position = (
                    ray * cst.SCALE,
                    0,
                )
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

    def render_gun(self, player: Player, target, game_map):
        self.screen.blit(*player.current_weapon.draw_gun())
        # Draw flare if gun has fired
        if player.current_weapon.in_progress:
            if player.current_weapon.dealing_damage:
                if target[-1][-1].hp and raycast_interact(
                    target[-1][-1].position, game_map, player.pos
                ):
                    target[-1][-1].take_damage(player.current_weapon.damage)
                player.current_weapon.dealing_damage = False
            self.render_flare(target[:-1], player)

    def render_flare(self, target, player):
        self.shot_proj = min(target, key=lambda x: x[1])[1] // 2
        shot = player.current_weapon.particles.draw_flare()
        if shot:
            shot = pygame.transform.scale(shot, (self.shot_proj, self.shot_proj))
            rect = shot.get_rect()
            self.screen.blit(
                shot,
                (cst.WIDTH // 2 - rect.w // 2, cst.HALF_HEIGHT - rect.h // 2),
            )

    def render_ui(self, player: Player):
        # HP
        hp = f"Health: {player.hp}/{player.max_hp}"
        image = self.font.render(
            hp, 0, cst.TEXT_COLOR if player.hp > 10 else cst.RED_COLOR
        )
        x, y = image.get_size()
        self.screen.blit(image, (cst.WIDTH - 65 - x, cst.HEIGHT - 50 - y))
        # Ammo
        num = player.current_weapon.ammo
        ammo = f"Ammo: {num}"
        image = self.font.render(ammo, 0, cst.TEXT_COLOR if num else cst.RED_COLOR)
        x, y = image.get_size()
        self.screen.blit(image, (cst.WIDTH - 65 - x, cst.HEIGHT - 10 - y))

    def frame_count(self, clock):
        text = str(int(clock.get_fps()))
        image = self.font.render(text, 0, cst.TEXT_COLOR)
        self.screen.blit(image, (65, 10))
