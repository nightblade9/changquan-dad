import unittest
from unittest.mock import MagicMock, Mock

from constants import FOV_ALGO, FOV_LIGHT_WALLS
from game import Game
from model.config import config
from model.entities.party.player import Player
from model.entities.party.stallion import Stallion
from model.maps.area_map import AreaMap
from model.systems.system import ComponentSystem
from view.map_renderer import MapRenderer
from view.adapter.tdl_adapter import TdlAdapter

SCREEN_WIDTH = 50
SCREEN_HEIGHT = 50
MAP_WIDTH = 10
MAP_HEIGHT = 10
PANEL_HEIGHT = 10


class TestMapRenderer(unittest.TestCase):
    def setUp(self):
        Game.instance = Mock()
        Game.instance.game_messages = []
        Game.instance.mouse_coord = (0, 0)

    def test_render_marks_current_fov_as_explored(self):
        map = AreaMap(MAP_WIDTH, MAP_HEIGHT)

        # Player is at (0, 0)
        player = Player()

        # Mock the FOV tiles.
        light_radius = 5
        fov_tiles = []        

        for i in range(light_radius):
            fov_tiles.append((i, 0)) # horizontal ray
            fov_tiles.append((0, i)) # vertical ray

        # Sanity check: it's not explored yet
        for (x, y) in fov_tiles:
            self.assertFalse(map.tiles[x][y].is_explored)

        tdl_adapter = TdlAdapter(
            "Test Window",
            map=(MAP_WIDTH, MAP_HEIGHT),
            screen=(SCREEN_WIDTH, SCREEN_HEIGHT),
            panel=(SCREEN_WIDTH, PANEL_HEIGHT)
        )
        tdl_adapter.calculate_fov = MagicMock(return_value=fov_tiles)

        renderer = MapRenderer(player, tdl_adapter)
        Game.instance.area_map = map
        Game.instance.renderer = renderer
        Game.instance.ui = tdl_adapter
        renderer.render()

        # Just check straight horizontal/vertical, as per our expectation
        for (x, y) in fov_tiles:
            self.assertTrue(map.tiles[x][y].is_explored)

    def test_render_recalculates_fov_when_asked(self):
        map = AreaMap(MAP_WIDTH, MAP_HEIGHT)

        # Player is at (0, 0)
        player = Player()

        # Mock the FOV tiles.
        light_radius = config.data.player.lightRadius
        fov_tiles = []        

        for i in range(light_radius):
            fov_tiles.append((i, 0))  # horizontal ray
            fov_tiles.append((0, i))  # vertical ray

        tdl_adapter = TdlAdapter(
            "Test Window",
            map=(MAP_WIDTH, MAP_HEIGHT),
            screen=(SCREEN_WIDTH, SCREEN_HEIGHT),
            panel=(SCREEN_WIDTH, PANEL_HEIGHT)
        )
        tdl_adapter.calculate_fov = MagicMock(return_value=fov_tiles)

        renderer = MapRenderer(player, tdl_adapter)
        self.assertTrue(renderer.recompute_fov)
        Game.instance.area_map = map
        Game.instance.renderer = renderer
        Game.instance.ui = tdl_adapter
        renderer.render()  # calls calculate_fov
        
        self.assertFalse(renderer.recompute_fov)        
        tdl_adapter.calculate_fov.reset_mock()  # reset call count to 0
        renderer.render()  # doesn't call calculate_fov
        tdl_adapter.calculate_fov.assert_not_called()

        renderer.recompute_fov = True
        renderer.render()

        tdl_adapter.calculate_fov.assert_called_with(
            player.x, player.y, map.is_visible_tile, FOV_ALGO, light_radius, FOV_LIGHT_WALLS
        )
