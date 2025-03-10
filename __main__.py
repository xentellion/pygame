import pygame
from src import sprites, game_map, player, render, weapon
from src import global_vars as cst
from sys import exit


def starting_screen(screen, clock):
    font = pygame.font.Font("fonts/amazdoomright2.ttf", 150)
    text = ["YUUM", "Нажмите любую кнопку"]
    # bg = pygame.transform.scale(load_image("fon.jpg"), (cst.WIDTH, cst.HEIGHT))
    # screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

        screen.fill(cst.CEILING_COLOR)
        start_point = cst.WIDTH // 2 - font.get_height() * (int(1.5 * len(text)) - 1)
        for idx, strin in enumerate(text):
            image = font.render(strin, 0, cst.TEXT_COLOR)
            rect = image.get_size()
            height_shift = int(rect[1] * 1.5)
            width_shift = cst.WIDTH // 2 - rect[0] // 2
            screen.blit(
                image,
                (
                    width_shift,
                    start_point + height_shift * idx,
                    *rect,
                ),
            )
        pygame.display.flip()
        clock.tick(cst.FPS_LOCK)


def quit():
    pygame.quit()
    exit()


def main():
    pygame.init()
    screen = pygame.display.set_mode((cst.WIDTH, cst.HEIGHT))
    pygame.display.flip()

    running = True
    clock = pygame.time.Clock()

    starting_screen(screen, clock)

    cst.OBJECTS = sprites.Sprites()
    renderer = render.Render(screen=screen)
    level, player_pos = game_map.create_map(
        elements=cst.OBJECTS,
        level="maps/level1.txt",
        tile_size=cst.TILE,
    )
    weapon.get_weapons()
    this_player = player.Player(
        position=player_pos,
    )
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.mixer.music.load("audio/Doom OST (Touhou Soundfont) - E1M5 Suspense.mp3")

    pygame.mouse.set_visible(False)
    # pygame.event.set_grab(True)
    pygame.mixer.music.play(10)
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
        renderer.render_background(this_player)
        walls, aiming_point = renderer.render_walls(this_player, level)
        renderer.render_world(
            walls + [sprite.face_player(this_player) for sprite in cst.OBJECTS.obj_list]
        )
        renderer.render_gun(this_player, [aiming_point, cst.OBJECTS.hit_sprite], level)
        renderer.render_ui(this_player)
        if not __debug__:
            renderer.frame_count(clock=clock)
        pygame.display.flip()
        clock.tick(cst.FPS_LOCK)
    pygame.quit()


if __name__ == "__main__":
    main()
