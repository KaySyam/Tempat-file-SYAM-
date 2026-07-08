import pygame
import sys
import random
from collections import deque
from pathlib import Path

# 1. INISIALISASI & KONFIGURASI DASAR
pygame.init()
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

# Cetakan Labirin Asli (1=Dinding, 0=Makanan, 2=Kosong/Penjara, 3=Pintu Penjara, 4=Power Pellet)
MAP_TEMPLATE = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,4,1],
    [1,0,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1],
    [1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1],
    [1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    [1,1,1,0,1,0,1,1,1,1,3,1,1,1,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,1,2,2,2,2,2,2,2,1,0,0,0,0,0,1],
    [1,0,1,1,1,0,1,2,1,1,2,1,1,2,1,0,1,1,1,0,1],
    [1,0,0,0,1,0,1,2,1,2,2,2,1,2,1,0,1,0,0,0,1],
    [1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,0,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,0,1],
    [1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    [1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,1],
    [1,0,1,1,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1],
    [1,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1],
    [1,0,1,0,1,0,1,1,1,0,1,0,1,1,1,0,1,0,1,0,1],
    [1,4,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,4,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
]

# Salinan aktif untuk dimainkan
MAP = [row[:] for row in MAP_TEMPLATE]

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 680
HUD_HEIGHT = 40
GRID_SIZE = min(28, max(20, (SCREEN_WIDTH - 20) // len(MAP[0])), max(20, (SCREEN_HEIGHT - HUD_HEIGHT - 20) // len(MAP)))

WIDTH = len(MAP[0]) * GRID_SIZE
HEIGHT = (len(MAP) * GRID_SIZE) + HUD_HEIGHT
MAZE_OFFSET_X = max(0, (SCREEN_WIDTH - WIDTH) // 2)
MAZE_OFFSET_Y = max(0, (SCREEN_HEIGHT - HEIGHT) // 2) + HUD_HEIGHT

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pacman Python - Red Ghost Attack Edition")
CLOCK = pygame.time.Clock()
FPS = 60

# Warna
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)

# Membaca High Score
HS_FILE = BASE_DIR / "highscore.txt"
if HS_FILE.exists():
    with open(HS_FILE, "r") as f:
        try: high_score = int(f.read())
        except ValueError: high_score = 0
else:
    high_score = 0

pacman_speed = 120  # pixels per second (smooth)
pacman_radius = 12
pacman_x, pacman_y = GRID_SIZE + (GRID_SIZE // 2), GRID_SIZE + (GRID_SIZE // 2)
score = 0
direction = (0, 0)  
requested_direction = (0, 0)
pacman_facing = (1, 0)
font = pygame.font.SysFont("Arial", 22)
game_state = "PLAYING" 

def load_image(relative_path, size=None):
    full_path = ASSETS_DIR / relative_path
    try:
        image = pygame.image.load(str(full_path))
        if size: image = pygame.transform.scale(image, size)
        return image
    except pygame.error:
        return None

# Definisi Arah Gerak (x, y)
ghost_directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
JAIL_EXIT_X = 10 * GRID_SIZE + (GRID_SIZE // 2)
JAIL_EXIT_Y = 5 * GRID_SIZE + (GRID_SIZE // 2)

POWER_MODE_DURATION = 6000
POWER_PELLET_VALUE = 4
power_mode = False
power_mode_timer = 0
lives = 3
power_pellet_positions = [(19, 1), (1, 19), (19, 19)]
GHOST_RELEASE_TIMES = [0, 15000, 30000]
ghost_release_index = 0
ghost_release_timer = 0
GHOST_MODE_SWITCH_INTERVAL = 7000
ghost_mode = "scatter"
ghost_mode_timer = 0

pacman_frames = []
for frame_num in range(1, 6):
    frame = load_image(f"player/pacman_{frame_num}.png", (pacman_radius * 2, pacman_radius * 2))
    if frame: pacman_frames.append(frame)
pacman_frame_index = 0
animation_timer = 0

wall_tile_img = load_image("tile/wall.png", (GRID_SIZE, GRID_SIZE))
door_img = load_image("tile/door.png", (GRID_SIZE, GRID_SIZE))
dot_img = load_image("item/dot.png", (8, 8))

ghosts = [
    {"x": 10 * GRID_SIZE + (GRID_SIZE // 2), "y": 7 * GRID_SIZE + (GRID_SIZE // 2), "color": RED, "dir": (0, -1), "speed": 110, "radius": 12, "name": "Blinky", "style": "chase", "frightened": False, "home_x": 10 * GRID_SIZE + (GRID_SIZE // 2), "home_y": 7 * GRID_SIZE + (GRID_SIZE // 2), "img": load_image("ghost/ghost_blinky.png", (24, 24)), "released": False},
    {"x": 11 * GRID_SIZE + (GRID_SIZE // 2), "y": 7 * GRID_SIZE + (GRID_SIZE // 2), "color": ORANGE, "dir": (0, -1), "speed": 85, "radius": 12, "name": "Clyde", "style": "clyde", "frightened": False, "home_x": 11 * GRID_SIZE + (GRID_SIZE // 2), "home_y": 7 * GRID_SIZE + (GRID_SIZE // 2), "img": load_image("ghost/ghost_clyde.png", (24, 24)), "released": False},
    {"x": 9 * GRID_SIZE + (GRID_SIZE // 2), "y": 7 * GRID_SIZE + (GRID_SIZE // 2), "color": PINK, "dir": (0, -1), "speed": 95, "radius": 12, "name": "Pinky", "style": "ambush", "frightened": False, "home_x": 9 * GRID_SIZE + (GRID_SIZE // 2), "home_y": 7 * GRID_SIZE + (GRID_SIZE // 2), "img": load_image("ghost/ghost_pinky.png", (24, 24)), "released": False}
]

def get_cell_value(x, y):
    col = max(0, min(len(MAP[0]) - 1, int(x // GRID_SIZE)))
    row = max(0, min(len(MAP) - 1, int(y // GRID_SIZE)))
    return MAP[row][col]


def world_to_tile(x, y):
    col = max(0, min(len(MAP[0]) - 1, int(x // GRID_SIZE)))
    row = max(0, min(len(MAP) - 1, int(y // GRID_SIZE)))
    return col, row


def tile_center(col, row):
    return col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2

def check_collision(x, y, radius, ignore_jail_door=False):
    sample_points = [
        (x, y), (x - radius, y), (x + radius, y),
        (x, y - radius), (x, y + radius)
    ]
    for px, py in sample_points:
        val = get_cell_value(px, py)
        if val == 1: return True
        if val == 3 and not ignore_jail_door: return True
    return False

def save_high_score(new_high):
    with open(HS_FILE, "w") as f: 
        f.write(str(new_high))

def can_move_towards(x, y, dx, dy, radius, ignore_jail=False):
    return not check_collision(x + dx, y + dy, radius, ignore_jail_door=ignore_jail)


def find_path_to_target(start_x, start_y, target_x, target_y, allow_jail_door=False):
    start_col, start_row = world_to_tile(start_x, start_y)
    target_col, target_row = world_to_tile(target_x, target_y)

    if (start_col, start_row) == (target_col, target_row):
        return []

    queue = deque([(start_col, start_row)])
    visited = {(start_col, start_row)}
    parents = {}

    while queue:
        col, row = queue.popleft()
        for dx, dy in ghost_directions:
            next_col = col + dx
            next_row = row + dy
            if not (0 <= next_col < len(MAP[0]) and 0 <= next_row < len(MAP)):
                continue
            if (next_col, next_row) in visited:
                continue

            cell_value = MAP[next_row][next_col]
            if cell_value == 1:
                continue
            if cell_value == 3 and not allow_jail_door:
                continue

            visited.add((next_col, next_row))
            parents[(next_col, next_row)] = (col, row)

            if (next_col, next_row) == (target_col, target_row):
                path = []
                cur = (next_col, next_row)
                while cur != (start_col, start_row):
                    path.append(cur)
                    cur = parents[cur]
                path.reverse()
                return path

            queue.append((next_col, next_row))

    return []


def choose_ghost_direction(ghost, target_x, target_y, ignore_jail=False, flee=False):
    current_val = get_cell_value(ghost["x"], ghost["y"])

    if current_val in (2, 3):
        ignore_jail = True
        target_x, target_y = JAIL_EXIT_X, JAIL_EXIT_Y

    valid_dirs = [d for d in ghost_directions if can_move_towards(ghost["x"], ghost["y"], d[0] * GRID_SIZE, d[1] * GRID_SIZE, ghost["radius"], ignore_jail=ignore_jail)]
    if not valid_dirs:
        return (0, 0)

    if current_val in (2, 3) and not flee:
        target_col, target_row = world_to_tile(target_x, target_y)

        def jail_direction_cost(d):
            nx = ghost["x"] + d[0] * GRID_SIZE
            ny = ghost["y"] + d[1] * GRID_SIZE
            ncol, nrow = world_to_tile(nx, ny)
            return abs(ncol - target_col) + abs(nrow - target_row)

        if ghost["dir"] in valid_dirs:
            return ghost["dir"]
        return min(valid_dirs, key=jail_direction_cost) if valid_dirs else (0, 0)

    current_col, current_row = world_to_tile(ghost["x"], ghost["y"])
    if ghost["name"] == "Blinky" and not flee:
        path = find_path_to_target(ghost["x"], ghost["y"], target_x, target_y, allow_jail_door=True)
        if path:
            next_col, next_row = path[0]
            next_dir = (next_col - current_col, next_row - current_row)
            if next_dir in valid_dirs:
                return next_dir

        target_col, target_row = world_to_tile(target_x, target_y)

        def blinky_direction_cost(d):
            nx = ghost["x"] + d[0] * GRID_SIZE
            ny = ghost["y"] + d[1] * GRID_SIZE
            ncol, nrow = world_to_tile(nx, ny)
            return abs(ncol - target_col) + abs(nrow - target_row)

        return min(valid_dirs, key=blinky_direction_cost)

    if ghost["name"] == "Blinky" and ghost["dir"] in valid_dirs:
        return ghost["dir"]

    if ghost["style"] != "random" and not flee:
        path = find_path_to_target(ghost["x"], ghost["y"], target_x, target_y, allow_jail_door=True)
        if path:
            next_col, next_row = path[0]
            next_dir = (next_col - current_col, next_row - current_row)
            if next_dir in valid_dirs:
                return next_dir

    reverse_dir = (-ghost["dir"][0], -ghost["dir"][1])
    if len(valid_dirs) > 1 and reverse_dir in valid_dirs:
        valid_dirs.remove(reverse_dir)

    if ghost["style"] == "random" or flee:
        return random.choice(valid_dirs)

    target_col, target_row = world_to_tile(target_x, target_y)

    def direction_cost(d):
        nx = ghost["x"] + d[0] * GRID_SIZE
        ny = ghost["y"] + d[1] * GRID_SIZE
        ncol, nrow = world_to_tile(nx, ny)
        return abs(ncol - target_col) + abs(nrow - target_row)

    if ghost["dir"] in valid_dirs:
        return ghost["dir"]

    return min(valid_dirs, key=direction_cost)

def get_ghost_target(ghost, pacman_x, pacman_y, direction):
    if ghost["name"] == "Blinky":
        pacman_col, pacman_row = world_to_tile(pacman_x, pacman_y)
        return tile_center(pacman_col, pacman_row)

    if ghost["style"] == "chase":
        if ghost_mode == "scatter":
            return tile_center(1, 1)
        return pacman_x, pacman_y

    if ghost["name"] == "Pinky" or ghost["style"] == "ambush":
        if ghost_mode == "scatter":
            return tile_center(1, 1)
        ahead = 4
        if direction == (0, 0):
            return pacman_x, pacman_y
        tx = pacman_x + direction[0] * GRID_SIZE * ahead
        ty = pacman_y + direction[1] * GRID_SIZE * ahead
        return tx, ty

    if ghost["style"] == "clyde":
        if ghost_mode == "scatter":
            return tile_center(1, len(MAP) - 2)
        gx, gy = ghost["x"], ghost["y"]
        dist = abs(gx - pacman_x) + abs(gy - pacman_y)
        if dist > GRID_SIZE * 8:
            return pacman_x, pacman_y
        return tile_center(1, len(MAP) - 2)

    return pacman_x, pacman_y

def draw_wall_tile(surface, x, y):
    render_x = x + MAZE_OFFSET_X
    render_y = y + MAZE_OFFSET_Y
    if wall_tile_img:
        surface.blit(wall_tile_img, (render_x, render_y))
    else:
        pygame.draw.rect(surface, BLUE, (render_x, render_y, GRID_SIZE, GRID_SIZE), 2)

def reset_game():
    global pacman_x, pacman_y, direction, requested_direction, game_state, ghosts, MAP, power_mode, power_mode_timer, ghost_release_index, ghost_release_timer
    pacman_x, pacman_y = GRID_SIZE + (GRID_SIZE // 2), GRID_SIZE + (GRID_SIZE // 2)
    direction = (0, 0)
    requested_direction = (0, 0)
    game_state = "PLAYING"
    power_mode = False
    power_mode_timer = 0
    ghost_release_index = 0
    ghost_release_timer = pygame.time.get_ticks()
    MAP = [row[:] for row in MAP_TEMPLATE]

    for ghost in ghosts:
        ghost["x"] = ghost["home_x"]
        ghost["y"] = ghost["home_y"]
        ghost["dir"] = (0, -1)
        ghost["frightened"] = False
        ghost["released"] = False
        ghost["patrol_index"] = 0

    global ghost_mode, ghost_mode_timer
    ghost_mode = "scatter"
    ghost_mode_timer = pygame.time.get_ticks()


def draw_maze(surface):
    for row_idx, row in enumerate(MAP):
        for col_idx, cell in enumerate(row):
            x = col_idx * GRID_SIZE + MAZE_OFFSET_X
            y = row_idx * GRID_SIZE + MAZE_OFFSET_Y
            if cell == 1:
                if wall_tile_img:
                    surface.blit(wall_tile_img, (x, y))
                else:
                    pygame.draw.rect(surface, BLUE, (x, y, GRID_SIZE, GRID_SIZE), 2)
            elif cell == POWER_PELLET_VALUE:
                center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)
                pygame.draw.circle(surface, ORANGE, center, 7)
                pygame.draw.circle(surface, WHITE, center, 3)
            elif cell == 0:
                if dot_img:
                    dot_rect = dot_img.get_rect(center=(x + GRID_SIZE // 2, y + GRID_SIZE // 2))
                    surface.blit(dot_img, dot_rect)
                else:
                    pygame.draw.circle(surface, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 2)
            elif cell == 3:
                if door_img:
                    surface.blit(door_img, (x, y))
                else:
                    pygame.draw.rect(surface, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)


def draw_hud(surface):
    hud = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT))
    hud.fill(BLACK)
    text = font.render(f"Score: {score}   High: {high_score}   Lives: {lives}", True, WHITE)
    hud.blit(text, (16, 8))
    if power_mode:
        power_text = font.render("POWER MODE", True, ORANGE)
        hud.blit(power_text, (SCREEN_WIDTH - 150, 8))
    surface.blit(hud, (0, 0))


def draw_player(surface):
    if pacman_frames:
        frame = pacman_frames[pacman_frame_index]
        # determine angle from facing
        facing = pacman_facing if 'pacman_facing' in globals() else direction
        if facing == (1, 0):
            angle = 0
        elif facing == (-1, 0):
            angle = 180
        elif facing == (0, -1):
            angle = 90
        elif facing == (0, 1):
            angle = 270
        else:
            angle = 0
        rotated = pygame.transform.rotate(frame, angle)
        rect = rotated.get_rect(center=(pacman_x + MAZE_OFFSET_X, pacman_y + MAZE_OFFSET_Y))
        surface.blit(rotated, rect)
    else:
        pygame.draw.circle(surface, YELLOW, (int(pacman_x + MAZE_OFFSET_X), int(pacman_y + MAZE_OFFSET_Y)), pacman_radius)


def draw_ghost(surface, ghost):
    if ghost["img"]:
        rect = ghost["img"].get_rect(center=(ghost["x"] + MAZE_OFFSET_X, ghost["y"] + MAZE_OFFSET_Y))
        surface.blit(ghost["img"], rect)
    else:
        pygame.draw.circle(surface, ghost["color"], (int(ghost["x"] + MAZE_OFFSET_X), int(ghost["y"] + MAZE_OFFSET_Y)), ghost["radius"])


def lose_life():
    global lives, game_state
    lives -= 1
    if lives <= 0:
        game_state = "GAME_OVER"
    else:
        reset_game()
        game_state = "PLAYING"


def get_tile_center(x, y):
    col = int(x // GRID_SIZE)
    row = int(y // GRID_SIZE)
    return col * GRID_SIZE + GRID_SIZE // 2, row * GRID_SIZE + GRID_SIZE // 2


def release_next_ghost():
    global ghost_release_index, ghost_release_timer
    if ghost_release_index >= len(GHOST_RELEASE_TIMES):
        return
    if pygame.time.get_ticks() - ghost_release_timer < GHOST_RELEASE_TIMES[ghost_release_index]:
        return

    ghost = ghosts[ghost_release_index]
    ghost["released"] = True
    ghost_release_index += 1
    ghost_release_timer = pygame.time.get_ticks()


def update_ghost_mode():
    global ghost_mode, ghost_mode_timer
    if power_mode or ghost_mode_timer == 0:
        return
    if pygame.time.get_ticks() - ghost_mode_timer > GHOST_MODE_SWITCH_INTERVAL:
        ghost_mode = "chase" if ghost_mode == "scatter" else "scatter"
        ghost_mode_timer = pygame.time.get_ticks()


def update_ghosts():
    release_next_ghost()
    update_ghost_mode()
    for ghost in ghosts:
        if not ghost["released"]:
            continue

        if not power_mode and ghost["frightened"]:
            ghost["frightened"] = False

        center_x, center_y = get_tile_center(ghost["x"], ghost["y"])
        current_val = get_cell_value(ghost["x"], ghost["y"])
        ignore_jail = current_val in (2, 3)
        # Recalculate when at or near tile center (use a fraction of GRID_SIZE)
        recalc_threshold = max(2, GRID_SIZE // 4)
        should_recalc = (
            ghost["dir"] == (0, 0)
            or (abs(ghost["x"] - center_x) < recalc_threshold and abs(ghost["y"] - center_y) < recalc_threshold)
            or not can_move_towards(ghost["x"], ghost["y"], ghost["dir"][0] * GRID_SIZE, ghost["dir"][1] * GRID_SIZE, ghost["radius"], ignore_jail=ignore_jail)
        )

        # Force Blinky to recalculate more frequently during chase
        if ghost["name"] == "Blinky" and ghost_mode == "chase":
            should_recalc = True

        if should_recalc:
            target_x, target_y = get_ghost_target(ghost, pacman_x, pacman_y, direction)

            if ghost["frightened"]:
                new_dir = choose_ghost_direction(ghost, target_x, target_y, ignore_jail=ignore_jail, flee=True)
            else:
                new_dir = choose_ghost_direction(ghost, target_x, target_y, ignore_jail=ignore_jail)

            if new_dir != (0, 0):
                ghost["dir"] = new_dir

        # move based on speed and direction (dt required from main loop)
        # If dt isn't provided (fallback), move by 1 pixel step
        try:
            dt_local = _dt
        except NameError:
            dt_local = 1.0 / FPS

        current_val = get_cell_value(ghost["x"], ghost["y"])
        ignore_jail = ghost["released"] or current_val in (2, 3)

        move_x = ghost["dir"][0] * ghost["speed"] * dt_local
        move_y = ghost["dir"][1] * ghost["speed"] * dt_local
        if can_move_towards(ghost["x"], ghost["y"], move_x, move_y, ghost["radius"], ignore_jail=ignore_jail):
            ghost["x"] += move_x
            ghost["y"] += move_y


def check_player_ghost_collision():
    global score, high_score
    for ghost in ghosts:
        distance = ((pacman_x - ghost["x"]) ** 2 + (pacman_y - ghost["y"]) ** 2) ** 0.5
        if distance <= pacman_radius + ghost["radius"]:
            if power_mode and ghost["frightened"]:
                ghost["x"] = ghost["home_x"]
                ghost["y"] = ghost["home_y"]
                ghost["dir"] = (0, -1)
                ghost["frightened"] = False
                score += 200
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)
            else:
                lose_life()
                return True
    return False


def check_win():
    return all(cell not in (0, POWER_PELLET_VALUE) for row in MAP for cell in row)


reset_game()

# 5. GAME LOOP UTAMA
while True:
    # frame timing for smooth movement
    dt = CLOCK.tick(FPS) / 1000.0
    _dt = dt
    SCREEN.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if game_state in ["GAME_OVER", "WIN"]:
                if event.key == pygame.K_r:
                    lives = 3
                    score = 0
                    reset_game()
            else:
                if event.key == pygame.K_UP:
                    requested_direction = (0, -1)
                elif event.key == pygame.K_DOWN:
                    requested_direction = (0, 1)
                elif event.key == pygame.K_LEFT:
                    requested_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    requested_direction = (1, 0)

    if game_state == "PLAYING":
        center_x, center_y = get_tile_center(pacman_x, pacman_y)
        # only allow changing direction when near tile center
        if abs(pacman_x - center_x) < 2 and abs(pacman_y - center_y) < 2:
            if requested_direction != (0, 0) and can_move_towards(pacman_x, pacman_y, requested_direction[0] * GRID_SIZE, requested_direction[1] * GRID_SIZE, pacman_radius):
                direction = requested_direction
                pacman_facing = direction

        if direction != (0, 0):
            move_x = direction[0] * pacman_speed * dt
            move_y = direction[1] * pacman_speed * dt
            if can_move_towards(pacman_x, pacman_y, move_x, move_y, pacman_radius):
                pacman_x += move_x
                pacman_y += move_y
            else:
                direction = (0, 0)

        animation_timer += 1
        if animation_timer % 8 == 0:
            pacman_frame_index = (pacman_frame_index + 1) % len(pacman_frames) if pacman_frames else 0

        current_col = max(0, min(len(MAP[0]) - 1, int(pacman_x // GRID_SIZE)))
        current_row = max(0, min(len(MAP) - 1, int(pacman_y // GRID_SIZE)))

        cell_value = MAP[current_row][current_col]
        if cell_value in (0, POWER_PELLET_VALUE):
            MAP[current_row][current_col] = 2
            if (current_col, current_row) in power_pellet_positions:
                score += 50
                power_mode = True
                power_mode_timer = pygame.time.get_ticks()
                for ghost in ghosts:
                    ghost["frightened"] = True
            else:
                score += 10

            if score > high_score:
                high_score = score
                save_high_score(high_score)

        if power_mode and pygame.time.get_ticks() - power_mode_timer > POWER_MODE_DURATION:
            power_mode = False

        update_ghosts()
        check_player_ghost_collision()

        if check_win():
            game_state = "WIN"

    draw_maze(SCREEN)
    draw_hud(SCREEN)
    draw_player(SCREEN)
    for ghost in ghosts:
        draw_ghost(SCREEN, ghost)

    if game_state == "GAME_OVER":
        over_text = pygame.font.SysFont("Arial", 36, True).render("GAME OVER", True, RED)
        SCREEN.blit(over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20))
        restart_text = font.render("Press R to restart", True, WHITE)
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 20))
    elif game_state == "WIN":
        win_text = pygame.font.SysFont("Arial", 36, True).render("YOU WIN!", True, YELLOW)
        SCREEN.blit(win_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 20))
        restart_text = font.render("Press R to restart", True, WHITE)
        SCREEN.blit(restart_text, (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 + 20))

    pygame.display.flip()
