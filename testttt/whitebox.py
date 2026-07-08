import os
import sys
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import simplepacman

class WhiteboxTests(unittest.TestCase):
    def setUp(self):
        simplepacman.reset_game()

    
    def test_ghosts_are_initialized_from_standard_list_structure(self):
        """Uji whitebox: inisialisasi hantu menggunakan struktur list biasa, bukan single linked list."""
        self.assertIsInstance(simplepacman.ghosts, list)
        self.assertEqual(len(simplepacman.ghosts), 3)
        self.assertEqual([ghost["name"] for ghost in simplepacman.ghosts], ["Blinky", "Clyde", "Pinky"])

    def test_get_cell_value_returns_wall(self):
        self.assertEqual(simplepacman.get_cell_value(0, 0), 1)

    def test_get_cell_value_returns_food(self):
        self.assertEqual(simplepacman.get_cell_value(simplepacman.GRID_SIZE, simplepacman.GRID_SIZE), 0)

    def test_check_collision_detects_wall(self):
        self.assertTrue(simplepacman.check_collision(0, 0, simplepacman.pacman_radius))

    def test_check_collision_allows_open_space(self):
        self.assertFalse(simplepacman.check_collision(simplepacman.GRID_SIZE + 8, simplepacman.GRID_SIZE + 8, simplepacman.pacman_radius))

    def test_can_move_towards_open_space(self):
        x, y = simplepacman.GRID_SIZE + 8, simplepacman.GRID_SIZE + 8
        self.assertTrue(simplepacman.can_move_towards(x, y, 2, 0, simplepacman.pacman_radius))

    def test_can_move_towards_wall_returns_false(self):
        x, y = simplepacman.GRID_SIZE + 8, simplepacman.GRID_SIZE + 8
        self.assertFalse(simplepacman.can_move_towards(x, y, 0, -simplepacman.GRID_SIZE, simplepacman.pacman_radius))

    def test_reset_game_restores_default_state(self):
        simplepacman.score = 500
        simplepacman.lives = 1
        simplepacman.game_state = "GAME_OVER"
        simplepacman.power_mode = True

        simplepacman.reset_game()

        self.assertEqual(simplepacman.score, 0)
        self.assertEqual(simplepacman.lives, 3)
        self.assertEqual(simplepacman.game_state, "PLAYING")
        self.assertFalse(simplepacman.power_mode)

    def test_choose_ghost_direction_prefers_target_direction(self):
        ghost = {
            "x": 2 * simplepacman.GRID_SIZE + 8,
            "y": 1 * simplepacman.GRID_SIZE + 8,
            "radius": simplepacman.pacman_radius,
            "dir": (2, 0),
        }

        direction = simplepacman.choose_ghost_direction(ghost, ghost["x"] + 100, ghost["y"])
        self.assertEqual(direction, (2, 0))

    def test_choose_ghost_direction_flee_avoids_target(self):
        ghost = {
            "x": 2 * simplepacman.GRID_SIZE + 8,
            "y": 1 * simplepacman.GRID_SIZE + 8,
            "radius": simplepacman.pacman_radius,
            "dir": (2, 0),
        }

        direction = simplepacman.choose_ghost_direction(ghost, ghost["x"] + 100, ghost["y"], flee=True)
        self.assertNotEqual(direction, (2, 0))

    def test_choose_ghost_direction_returns_zero_when_trapped(self):
        ghost = {"x": 0, "y": 0, "radius": simplepacman.pacman_radius, "dir": (0, 0)}
        direction = simplepacman.choose_ghost_direction(ghost, 100, 100)
        self.assertEqual(direction, (0, 0))

    def test_get_ghost_target_for_non_ambush_ghost(self):
        ghost = {"style": "random"}
        target = simplepacman.get_ghost_target(ghost, 100, 100, (2, 0))
        self.assertEqual(target, (100, 100))

    def test_get_ghost_target_for_ambush_ghost(self):
        ghost = {"style": "ambush"}
        target = simplepacman.get_ghost_target(ghost, 100, 100, (2, 0))
        self.assertEqual(target, (100 + 2 * simplepacman.GRID_SIZE * 2, 100))

if __name__ == "__main__":
    unittest.main(verbosity=2)
