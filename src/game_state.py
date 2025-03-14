import src.global_vars as cst
from math import dist


def win_condition():
    # You cannot win unless you shoot every fairy!
    enemies = list(filter(lambda x: x.npc, cst.OBJECTS.obj_list))
    if len(enemies) == 0:
        cst.EXIT_OPEN = True
        print("DOOR OPEN")


def exit_check():
    if cst.EXIT_OPEN:
        distance = dist(cst.PLAYER.pos, cst.EXIT_POINT)
        if distance < cst.TILE / 2:
            return True
    return False
