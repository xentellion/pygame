from math import atan2, pi, sin, cos
import src.global_vars as cst


class Interactable:
    def __init__():
        pass


def raycast_interact(npc_pos, game_map, player_pos):
    npc_x, npc_y = npc_pos
    ox, oy = player_pos
    xm, ym = cst.mapping(ox, oy)
    delta_x, delta_y = ox - npc_x, oy - npc_y
    cur_angle = atan2(delta_y, delta_x)
    cur_angle += pi

    if not (sin_a := sin(cur_angle)):
        sin_a = cst.EPSILON
    if not (cos_a := cos(cur_angle)):
        cos_a = cst.EPSILON

    # verticals
    x, dx = (xm + cst.TILE, 1) if cos_a >= 0 else (xm, -1)
    for i in range(0, int(abs(delta_x)) // cst.TILE):
        depth_v = (x - ox) / cos_a
        yv = oy + depth_v * sin_a
        tile_v = cst.mapping(x + dx, yv)
        if tile_v in game_map:
            return False
        x += dx * cst.TILE

    # horizontals
    y, dy = (ym + cst.TILE, 1) if sin_a >= 0 else (ym, -1)
    for i in range(0, int(abs(delta_y)) // cst.TILE):
        depth_h = (y - oy) / sin_a
        xh = ox + depth_h * cos_a
        tile_h = cst.mapping(xh, y + dy)
        if tile_h in game_map:
            return False
        y += dy * cst.TILE
    return True
