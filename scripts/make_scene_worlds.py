#!/usr/bin/env python3
"""Write ground/light variants of platform_world.sdf from scene_variants.json.

Only the ground colour, the sun and the scene ambient change; world name,
drone, platforms and parked distractors stay identical to the base world.
"""

import json
from pathlib import Path
import xml.etree.ElementTree as ET

WORLDS = Path(__file__).resolve().parents[1] / 'sim' / 'worlds'
BASE = WORLDS / 'platform_world.sdf'


def world_name(ground, light):
    """Return the ALIGN_WORLD name for one ground/light pair."""
    return f'platform_world_{ground}_{light}'


def build(ground, light):
    """Return the base world tree with one ground and one light applied."""
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    tree = ET.parse(BASE, parser)
    world = tree.getroot().find('world')

    material = world.find(".//visual[@name='ground_visual']/material")
    material.find('ambient').text = f"{ground['color']} 1"
    material.find('diffuse').text = f"{ground['color']} 1"

    sun = world.find("light[@name='sun']")
    sun.find('direction').text = light['direction']
    sun.find('diffuse').text = f"{light['diffuse']} 1"
    sun.find('specular').text = f"{light['diffuse']} 1"
    sun.find('cast_shadows').text = str(light['cast_shadows']).lower()

    world.find('scene/ambient').text = light['scene_ambient']
    return tree


def main():
    variants = json.loads((WORLDS / 'scene_variants.json').read_text())
    base = variants['base']
    for ground_key, ground in variants['grounds'].items():
        for light_key, light in variants['lights'].items():
            if (ground_key, light_key) == (base['ground'], base['light']):
                continue
            name = world_name(ground_key, light_key)
            body = ET.tostring(build(ground, light).getroot(), encoding='unicode')
            header = (
                '<?xml version="1.0" ?>\n'
                '<!-- Generated from platform_world.sdf by scripts/make_scene_worlds.py '
                f'({ground["variant"]}, {light["variant"]}). Do not edit by hand. -->\n'
            )
            path = WORLDS / f'{name}.sdf'
            path.write_text(header + body + '\n', encoding='utf-8')
            print(path.name)


if __name__ == '__main__':
    main()
