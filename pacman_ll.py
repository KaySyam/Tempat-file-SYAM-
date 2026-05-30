import pygame
import sys

# 1. Struktur Node untuk Singly Linked List
class Node:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.next = None

class LinkedList:
    def __init__(self, x, y):
        self.head = Node(x, y)

    def set_pos(self, x, y):
        self.head.x, self.head.y = x, y

# 2. Inisialisasi Pygame & Arena
pygame.init()
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
# Ubah maze ke list agar dot bisa dihapus
grid = [list(row) for row in MAZE]

WIDTH, HEIGHT = len(grid[0]) * TILE_SIZE, len(grid) * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Linked List - Score System")

# Warna & Font
YELLOW, RED, BLUE, BLACK, WHITE = (255, 255, 0), (255, 0, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)
font = pygame.font.SysFont("Arial", 18, bold=True)

# Karakter (Menggunakan Linked List)
pacman = LinkedList(TILE_SIZE, TILE_SIZE)
ghost = LinkedList(TILE_SIZE * 18, TILE_SIZE * 9)
score = 0
p_dir = [0, 0]

def can_move(x, y):
    # Cek tabrakan dinding berbasis grid
    gx, gy = int(x // TILE_SIZE), int(y // TILE_SIZE)
    if 0 <= gy < len(grid) and 0 <= gx < len(grid[0]):
        return grid[gy][gx] != "#"
    return False

clock = pygame.time.Clock()

# 3. Main Loop
while True:
    screen.fill(BLACK)
    
    # Gambar Labirin & Dot
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == "#":
                pygame.draw.rect(screen, BLUE, (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
            elif cell == ".":
                pygame.draw.circle(screen, WHITE, (c*TILE_SIZE + TILE_SIZE//2, r*TILE_SIZE + TILE_SIZE//2), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: p_dir = [-2, 0]
            if event.key == pygame.K_RIGHT: p_dir = [2, 0]
            if event.key == pygame.K_UP: p_dir = [0, -2]
            if event.key == pygame.K_DOWN: p_dir = [0, 2]

    # Update Pac-Man
    nx, ny = pacman.head.x + p_dir[0], pacman.head.y + p_dir[1]
    # Cek sisi kanan/bawah karakter juga (padding)
    if can_move(nx, ny) and can_move(nx+20, ny+20):
        pacman.set_pos(nx, ny)

    # Logika Skor (Makan Dot)
    curr_gx, curr_gy = int((pacman.head.x+15)//TILE_SIZE), int((pacman.head.y+15)//TILE_SIZE)
    if grid[curr_gy][curr_gx] == ".":
        grid[curr_gy][curr_gx] = " "
        score += 10

    # Gerakan Musuh (Ghost)
    gx, gy = ghost.head.x, ghost.head.y
    if gx < pacman.head.x: gx += 1
    elif gx > pacman.head.x: gx -= 1
    if gy < pacman.head.y: gy += 1
    elif gy > pacman.head.y: gy -= 1
    if can_move(gx, gy): ghost.set_pos(gx, gy)

    # Gambar Karakter & Skor
    pygame.draw.circle(screen, YELLOW, (int(pacman.head.x+15), int(pacman.head.y+15)), 12)
    pygame.draw.rect(screen, RED, (ghost.head.x+5, ghost.head.y+5, 20, 20))
    
    txt = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(txt, (10, 5))

    # Cek Game Over
    if abs(pacman.head.x - ghost.head.x) < 15 and abs(pacman.head.y - ghost.head.y) < 15:
        print(f"GAME OVER! Skor Akhir: {score}")
        pygame.quit(); sys.exit()

    pygame.display.flip()
    clock.tick(60)
