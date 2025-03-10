from src.sprites import PlacedObject, Sprites
import src.global_vars as cst
import json


def create_map(elements: Sprites, level="maps/level0.txt", tile_size=10):
    with open(level, "r", encoding="utf-8") as f:
        text = [line.strip() for line in f.readlines()]

    with open("configs/texture_map.json", "r", encoding="utf-8") as f:
        textures = json.load(f)

    with open("configs/sprite_map.json", "r", encoding="utf-8") as f:
        items = json.load(f)

    level_map = {}
    for y, row in enumerate(text):
        for x, tile in enumerate(row):
            if tile in (".", " "):
                continue
            if tile == "#":
                player_pos = ((x + 0.5) * tile_size, (y + 0.5) * tile_size)
                continue
            if tile in textures:
                level_map[(x * cst.TILE, y * cst.TILE)] = textures[tile]
            elif tile in items:
                elements.obj_list.append(
                    PlacedObject((x + 0.5, y + 0.5), **items[tile])
                )
    return level_map, player_pos
