import pygame
from src import objects, game_map, player, render, game_state
from src import global_vars as cst
from sys import exit
import json


def restart_level():
    cst.OBJECTS = objects.Objects()
    player_pos = game_map.create_map(
        elements=cst.OBJECTS,
        level="maps/level1.txt",
        tile_size=cst.TILE,
    )
    # yay a singleton
    if not cst.PLAYER:
        cst.PLAYER = player.Player(
            position=player_pos,
        )
    else:
        cst.PLAYER.restart(position=player_pos)
    pygame.mixer.init()
    pygame.mixer.music.load("audio/Doom OST (Touhou Soundfont) - E1M5 Suspense.mp3")
    pygame.mixer.music.play(10)


def quit():
    pygame.quit()
    exit()


def main():
    pygame.init()
    pygame.display.set_caption("Yuuka gaming")
    screen = pygame.display.set_mode((cst.WIDTH, cst.HEIGHT))
    pygame.display.flip()

    with open("configs/text.json", "r", encoding="utf-8") as f:
        cst.TEXT = json.load(f)

    running = True
    clock = pygame.time.Clock()

    renderer = render.Render(screen=screen)
    renderer.ui_screen(clock, cst.TEXT["start"])

    restart_level()

    pygame.mouse.set_visible(False)
    # pygame.event.set_grab(True)

    while running:
        # check statics
        renderer.render_background()
        walls, aiming_point = renderer.render_walls()
        renderer.render_world(
            walls + [sprite.face_player() for sprite in cst.OBJECTS.obj_list]
        )
        renderer.render_gun([aiming_point, cst.OBJECTS.hit_sprite()])
        renderer.render_ui()

        if __debug__:
            renderer.frame_count(clock=clock)

        if cst.GAME_OVER:
            for event in pygame.event.get():
                running = cst.PLAYER.quit(event)
            # Some graphic stuff
            if cst.PLAYER.lives <= 0:
                running = False
            else:
                restart_level()
                cst.GAME_OVER = None
        else:
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

            if cst.EXIT_OPEN:
                renderer.door_open()

            if game_state.exit_check():
                cst.GAME_OVER = False
                running = False
            pygame.display.flip()
        clock.tick(cst.FPS_LOCK)

    if cst.GAME_OVER:
        renderer.ui_screen(clock, cst.TEXT["fail"])
    elif cst.GAME_OVER is not None:
        renderer.ui_screen(clock, cst.TEXT["good" if cst.PLAYER.lives >= 3 else "bad"])

    pygame.quit()


if __name__ == "__main__":
    main()
