import sys
import array
import random
import math

class Node:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.next = None

class LinkedList:
    def __init__(self, x, y):
        self.head = Node(x, y)
    def set_pos(self, x, y):
        self.head.x, self.head.y = x, y

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

TILE_SIZE = 30
MAZE = [
    "####################",
    "#........##........#",
    "#.##.###.##.###.##.#",
    "#..................#",
    "#.##.#.######.#.##.#",
    "#....#...##...#....#",
    "####.###.##.###.####",
    "#........##........#",
    "#.######.##.######.#",
    "#..................#",
    "####################"
]

grid = [list(row) for row in MAZE]
WIDTH, HEIGHT = len(grid[0]) * TILE_SIZE, len(grid) * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Linked List")

YELLOW, RED, BLUE, BLACK, WHITE = (255, 255, 0), (255, 0, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)
GREEN = (0, 255, 0)
font = pygame.font.SysFont("Arial", 18, bold=True)
big_font = pygame.font.SysFont("Arial", 36, bold=True)

def generate_beep(frequency, duration_ms, volume=0.1):
    sample_rate = 22050
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    period = sample_rate / frequency
    buf = array.array('h', [0] * num_samples)
    for i in range(num_samples):
        if (i % period) < (period / 2):
            buf[i] = int(32767 * volume)
        else:
            buf[i] = int(-32768 * volume)
    return pygame.mixer.Sound(buffer=buf)

sound_eat = generate_beep(600, 50, 0.05)   
sound_win = generate_beep(800, 300, 0.1)   
sound_lose = generate_beep(150, 400, 0.15) 

def reset_game():
    global grid, pacman, ghost, score, total_dots, p_dir, next_dir, game_state, sound_played
    global mouth_angle, mouth_closing
    grid = [list(row) for row in MAZE]
    pacman = LinkedList(TILE_SIZE, TILE_SIZE)
    ghost = LinkedList(TILE_SIZE * 18, TILE_SIZE * 9)
    score = 0
    total_dots = sum(row.count(".") for row in grid)
    p_dir = [0, 0]
    next_dir = [0, 0]
    game_state = "PLAY"  
    sound_played = False
    mouth_angle = 0      
    mouth_closing = False

def can_move(x, y, dx, dy):
    margin = 4
    points = [
        (x + dx + margin, y + dy + margin),
        (x + dx + TILE_SIZE - 1 - margin, y + dy + margin),
        (x + dx + margin, y + dy + TILE_SIZE - 1 - margin),
        (x + dx + TILE_SIZE - 1 - margin, y + dy + TILE_SIZE - 1 - margin)
    ]
    for px, py in points:
        gx, gy = int(px // TILE_SIZE), int(py // TILE_SIZE)
        if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]):
            if grid[gy][gx] == "#": return False
        else: return False
    return True

reset_game()
clock = pygame.time.Clock()

while True:
    clock.tick(60)
    
    if game_state == "PLAY":
        screen.fill(BLACK)
        
        # Animasi buka tutup mulut
        if mouth_closing:
            mouth_angle -= 4
            if mouth_angle <= 0: mouth_angle = 0; mouth_closing = False
        else:
            mouth_angle += 4
            if mouth_angle >= 45: mouth_angle = 45; mouth_closing = True

        # Render Peta dan Dot
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                if cell == "#": pygame.draw.rect(screen, BLUE, (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
                elif cell == ".": pygame.draw.circle(screen, WHITE, (c*TILE_SIZE + TILE_SIZE//2, r*TILE_SIZE + TILE_SIZE//2), 3)

        # Kontrol Input
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: next_dir = [-3, 0]
                if event.key == pygame.K_RIGHT: next_dir = [3, 0]
                if event.key == pygame.K_UP: next_dir = [0, -3]
                if event.key == pygame.K_DOWN: next_dir = [0, 3]

        # Pergerakan Pacman
        if can_move(pacman.head.x, pacman.head.y, next_dir[0], next_dir[1]): p_dir = next_dir
        if can_move(pacman.head.x, pacman.head.y, p_dir[0], p_dir[1]):
            pacman.set_pos(pacman.head.x + p_dir[0], pacman.head.y + p_dir[1])

        # Makan Dot
        curr_gx = int((pacman.head.x + TILE_SIZE // 2) // TILE_SIZE)
        curr_gy = int((pacman.head.y + TILE_SIZE // 2) // TILE_SIZE)
        if 0 <= curr_gy < len(grid) and 0 <= curr_gx < len(grid[0]):
            if grid[curr_gy][curr_gx] == ".":
                grid[curr_gy][curr_gx] = " "
                score += 10; total_dots -= 1; sound_eat.play()  

        if total_dots <= 0: game_state = "WIN"

        # AI Hantu
        for _ in range(2): 
            possible_moves = []
            if ghost.head.x < pacman.head.x and can_move(ghost.head.x, ghost.head.y, 1, 0): possible_moves.append((1, 0))
            if ghost.head.x > pacman.head.x and can_move(ghost.head.x, ghost.head.y, -1, 0): possible_moves.append((-1, 0))
            if ghost.head.y < pacman.head.y and can_move(ghost.head.x, ghost.head.y, 0, 1): possible_moves.append((0, 1))
            if ghost.head.y > pacman.head.y and can_move(ghost.head.x, ghost.head.y, 0, -1): possible_moves.append((0, -1))

            if not possible_moves:
                all_dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                possible_moves = [(dx, dy) for dx, dy in all_dirs if can_move(ghost.head.x, ghost.head.y, dx, dy)]

            if possible_moves:
                chosen_move = random.choice(possible_moves)
                ghost.set_pos(ghost.head.x + chosen_move[0], ghost.head.y + chosen_move[1])

        # Deteksi Tabrakan (Game Over)
        if abs(pacman.head.x - ghost.head.x) < 18 and abs(pacman.head.y - ghost.head.y) < 18: game_state = "GAME_OVER"

        # RENDER PACMAN (Perbaikan logika sudut matematika)
        px, py = pacman.head.x + TILE_SIZE//2, pacman.head.y + TILE_SIZE//2
        radius = 12
        
        if p_dir[0] > 0: base_angle = 0      # Kanan
        elif p_dir[0] < 0: base_angle = 180  # Kiri
        elif p_dir[1] < 0: base_angle = 90   # Atas (Pygame arc kebalik)
        elif p_dir[1] > 0: base_angle = 270  # Bawah
        else: base_angle = 0

        # Menghitung awal dan akhir sudut yang benar (berlawanan arah jarum jam)
        start_angle = (base_angle + mouth_angle) % 360
        end_angle = (base_angle - mouth_angle) % 360
        if end_angle <= start_angle: end_angle += 360

        start_rad, end_rad = math.radians(start_angle), math.radians(end_angle)
        for r in range(1, radius + 1): 
            pygame.draw.arc(screen, YELLOW, (px - r, py - r, r * 2, r * 2), start_rad, end_rad, 2)

        # Render Hantu & Skor
        pygame.draw.rect(screen, RED, (ghost.head.x + 4, ghost.head.y + 4, 22, 22))
        txt = font.render(f"SCORE: {score}  |  DOTS LEFT: {total_dots}", True, WHITE)
        screen.blit(txt, (10, 5))

    else:
        # Layar Win / Game Over
        if not sound_played:
            if game_state == "GAME_OVER": sound_lose.play()
            elif game_state == "WIN": sound_win.play()
            sound_played = True

        screen.fill(BLACK)
        title_txt = big_font.render("GAME OVER" if game_state == "GAME_OVER" else "YOU WIN!", True, RED if game_state == "GAME_OVER" else GREEN)
        score_txt = font.render(f"Skor Akhir: {score}", True, WHITE)
        info_txt = font.render("Tekan [R] untuk Main Lagi  |  Tekan [Q] untuk Keluar", True, WHITE)
        
        screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(score_txt, (WIDTH // 2 - score_txt.get_width() // 2, HEIGHT // 2 + 5))
        screen.blit(info_txt, (WIDTH // 2 - info_txt.get_width() // 2, HEIGHT // 2 + 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: reset_game()
                if event.key == pygame.K_q: pygame.quit(); sys.exit()

    pygame.display.flip()