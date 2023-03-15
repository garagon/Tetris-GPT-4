import sys
import pygame
import random

# Configuración básica
SCREEN_WIDTH = 200
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 10
FONT_SIZE = 24

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHT_GRAY = (200, 200, 200)


# Colores de las piezas de Tetris
COLORS = [
    (0, 0, 0),      # No usar este color (índice 0)
    (0, 255, 255),  # I: cian
    (0, 0, 255),    # J: azul
    (255, 165, 0),  # L: naranja
    (255, 255, 0),  # O: amarillo
    (0, 255, 0),    # S: verde
    (128, 0, 128),  # T: morado
    (255, 0, 0),    # Z: rojo
]

PIECES = [
    (1, (0, 0), (1, 0), (2, 0), (3, 0)),  # I: cian
    (2, (0, 0), (1, 0), (2, 0), (2, 1)),  # J: azul
    (3, (0, 0), (1, 0), (2, 0), (0, 1)),  # L: naranja
    (4, (0, 0), (1, 0), (0, 1), (1, 1)),  # O: amarillo
    (5, (0, 0), (1, 0), (1, 1), (2, 1)),  # S: verde
    (6, (0, 0), (1, 0), (1, 1), (2, 1)),  # T: morado
    (7, (0, 0), (1, 0), (1, 1), (2, 1)),  # Z: rojo
]

def new_piece():
    return random.choice(PIECES)

def create_grid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid(screen):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y))

def draw_piece(screen, piece, x, y):
    piece_color = COLORS[piece[0]]
    for dx, dy in piece[1:]:
        new_x = x + dx * GRID_SIZE
        new_y = y + dy * GRID_SIZE
        pygame.draw.rect(screen, piece_color, (new_x, new_y, GRID_SIZE - 1, GRID_SIZE - 1))

def draw_board(screen, board):
    for row_idx, row in enumerate(board):
        for col_idx, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, BLUE, (col_idx * GRID_SIZE, row_idx * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)

def rotate_piece(piece):
    color_idx, *coords = piece
    return (color_idx, *[((-y, x) if (x, y) != (0, 0) else (x, y)) for x, y in coords])

def valid_move(board, piece, x, y):
    for dx, dy in piece[1:]:
        new_x = x + dx
        new_y = y + dy

        # Verificar si las coordenadas están dentro de los límites del tablero
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return False

        # Verificar si la posición está ocupada
        if board[new_y][new_x] != 0:
            return False

    return True

def freeze_piece(board, piece, x, y):
    for dx, dy in piece[1:]:
        new_x = x + dx
        new_y = y + dy
        board[new_y][new_x] = 1

def play_tetris_theme():
    pygame.mixer.init()
    pygame.mixer.music.load('Tetris.mp3')
    pygame.mixer.music.play(-1)  # Reproduce en bucle                

def clear_lines(board):
    lines_cleared = 0
    full_rows = []
    for row_idx, row in enumerate(board):
        if all(cell == 1 for cell in row):
            lines_cleared += 1
            full_rows.append(row_idx)

    if full_rows:
        for row_idx in full_rows:
            del board[row_idx]
            board.insert(0, [0 for _ in range(GRID_WIDTH)])

    return lines_cleared

def render_text(screen, text, color, x, y, font_size=FONT_SIZE):
    font = pygame.font.Font(pygame.font.get_default_font(), font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris GPT-4")
    clock = pygame.time.Clock()
    play_tetris_theme()

    board = create_grid()
    current_piece = new_piece()
    piece_x, piece_y = GRID_WIDTH // 2 - len(current_piece[1:]) // 2, 0


    score = 0
    delay = 500

    drop_time = pygame.time.get_ticks()

    while True:
        screen.fill(LIGHT_GRAY)  # Cambia BLACK por LIGHT_GRAY
        draw_grid(screen)
        draw_board(screen, board)
        draw_piece(screen, current_piece, piece_x * GRID_SIZE, piece_y * GRID_SIZE)
        render_text(screen, f"Score: {score}", WHITE, 10, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and valid_move(board, current_piece, piece_x - 1, piece_y):
            piece_x -= 1
        if keys[pygame.K_RIGHT] and valid_move(board, current_piece, piece_x + 1, piece_y):
            piece_x += 1
        if keys[pygame.K_DOWN] and valid_move(board, current_piece, piece_x, piece_y + 1):
            piece_y += 1
        if keys[pygame.K_UP]:
            rotated_piece = rotate_piece(current_piece)
            if valid_move(board, rotated_piece, piece_x, piece_y):
                current_piece = rotated_piece

        if pygame.time.get_ticks() - drop_time > delay:
            if valid_move(board, current_piece, piece_x, piece_y + 1):
                piece_y += 1
            else:
                freeze_piece(board, current_piece, piece_x, piece_y)
                lines_cleared = clear_lines(board)
                score += lines_cleared * 100
                print("Score:", score)
                current_piece = new_piece()
                piece_x, piece_y = GRID_WIDTH // 2 - len(current_piece[1]) // 2, 0
                if not valid_move(board, current_piece, piece_x, piece_y):
                    print("Game Over!")
                    pygame.quit()
                    sys.exit()
            drop_time = pygame.time.get_ticks()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()        