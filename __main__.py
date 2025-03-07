import pygame
from src import sprites, game_map, player, render, weapon
from src import global_vars as cst


def main():
    pygame.init()
    screen = pygame.display.set_mode((cst.WIDTH, cst.HEIGHT))
    pygame.display.flip()

    running = True
    clock = pygame.time.Clock()

    game_sprites = sprites.Sprites()
    renderer = render.Render(screen=screen)
    level, player_pos = game_map.create_map(
        elements=game_sprites,
        level="maps/level1.txt",
        tile_size=cst.TILE,
    )
    weapon.get_weapons()
    this_player = player.Player(
        position=player_pos,
    )

    pygame.mouse.set_visible(False)
    # pygame.event.set_grab(True)

    while running:
        # CONTROLS
        for event in pygame.event.get():
            running = this_player.quit(event)
            this_player.rotate(event)
            this_player.shoot(event)
            this_player.use(event)
        keys = pygame.key.get_pressed()
        this_player.move(clock=clock, keys=keys, colliders=level)
        # RENDER
        renderer.render_background()
        walls, aiming_point = renderer.render_walls(this_player, level)
        renderer.render_world(
            walls
            + [sprite.face_player(this_player) for sprite in game_sprites.obj_list]
        )
        renderer.render_gun(this_player, [aiming_point, game_sprites.hit_sprite])
        renderer.render_ui(this_player)

        renderer.frame_count(clock=clock)
        pygame.display.flip()
        clock.tick(cst.FPS_LOCK)
    pygame.quit()


if __name__ == "__main__":
    main()
