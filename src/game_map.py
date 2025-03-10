from src.objects import GameObject, Objects
from src.weapon import Weapon
import src.global_vars as cst
import json


def load_config(level):
    # Load map and textures in one place
    with open(level, "r", encoding="utf-8") as f:
        level_layout = [line.strip() for line in f.readlines()]
    with open("configs/texture_map.json", "r", encoding="utf-8") as f:
        textures = json.load(f)
    with open("configs/sprite_map.json", "r", encoding="utf-8") as f:
        objects = json.load(f)
    with open("configs/weapons.json", "r", encoding="utf-8") as f:
        weapons = json.load(f)
        for k, v in weapons.items():
            cst.WEAPONS[k] = Weapon(**v)
        # List[str], json dict, json dict
    return level_layout, textures, objects


def create_map(
    elements: Objects,
    level: str = "maps/level0.txt",
    tile_size: int = 10,
):
    # load level layout and data for everything
    level_layout, textures, objects = load_config(level)

    # dict (x, y) : element on that coord
    level_map = {}
    empty = (".", " ")
    for y, row in enumerate(level_layout):
        for x, tile in enumerate(row):
            if tile in empty:
                continue
            elif tile == "#":
                # 0.5 adjust otherwise it spawns in a (0, 0) corner of a tile
                player_pos = ((x + 0.5) * tile_size, (y + 0.5) * tile_size)
                continue
            elif tile in textures:
                level_map[(x * cst.TILE, y * cst.TILE)] = textures[tile]
            elif tile in objects:
                # same as for player
                elements.obj_list.append(
                    GameObject((x + 0.5, y + 0.5), **objects[tile])
                )
        cst.GAME_MAP = level_map
    return player_pos
