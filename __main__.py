import pygame
from src import objects, game_map, player, render
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
    pygame.display.set_caption("Yuuka gaming")
    screen = pygame.display.set_mode((cst.WIDTH, cst.HEIGHT))
    pygame.display.flip()

    running = True
    clock = pygame.time.Clock()

    starting_screen(screen, clock)

    renderer = render.Render(screen=screen)
    cst.OBJECTS = objects.Objects()

    player_pos = game_map.create_map(
        elements=cst.OBJECTS,
        level="maps/level1.txt",
        tile_size=cst.TILE,
    )

    # yay, a singleton (why though)
    if not cst.PLAYER:
        cst.PLAYER = player.Player(
            position=player_pos,
        )

    pygame.mixer.init()
    pygame.mixer.music.load("audio/Doom OST (Touhou Soundfont) - E1M5 Suspense.mp3")

    pygame.mouse.set_visible(False)
    # pygame.event.set_grab(True)
    pygame.mixer.music.play(10)

    while running:
        # check statics
        renderer.render_background()
        walls, aiming_point = renderer.render_walls()
        renderer.render_world(
            walls + [sprite.face_player() for sprite in cst.OBJECTS.obj_list]
        )
        renderer.render_gun([aiming_point, cst.OBJECTS.hit_sprite()])
        renderer.render_ui()

        # Player's turn
        for event in pygame.event.get():
            running = cst.PLAYER.quit(event)
            cst.PLAYER.rotate(event)
            cst.PLAYER.shoot(event, [aiming_point, cst.OBJECTS.hit_sprite()])
            cst.PLAYER.use(event)
        cst.PLAYER.move(clock=clock, keys=pygame.key.get_pressed())

        # NPC's turn
        for i in cst.OBJECTS.obj_list:
            if i.npc:
                i.move()

        if __debug__:
            renderer.frame_count(clock=clock)

        pygame.display.flip()
        clock.tick(cst.FPS_LOCK)
    pygame.quit()


if __name__ == "__main__":
    main()
