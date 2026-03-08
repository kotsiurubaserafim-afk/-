import pygame
import socket
import json

# Настройки графики
TILE_SIZE = 40
WIDTH, HEIGHT = 400, 300
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Сетевое подключение
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5555))

def get_server_data(dx=0, dy=0):
    move = json.dumps({"dx": dx, "dy": dy})
    client.send(move.encode('utf-8'))
    data = client.recv(4096).decode('utf-8')
    return json.loads(data)

running = True
# Получаем начальное состояние
game_state = get_server_data()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            elif event.key == pygame.K_DOWN: dy = 1
            elif event.key == pygame.K_LEFT: dx = -1
            elif event.key == pygame.K_RIGHT: dx = 1
            
            if dx != 0 or dy != 0:
                game_state = get_server_data(dx, dy)

    # Отрисовка
    screen.fill((50, 50, 50))
    maze = game_state['maze']
    player = game_state['player']

    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = (200, 200, 200) if cell == 1 else (30, 30, 30)
            pygame.draw.rect(screen, color, (x*TILE_SIZE, y*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1))

    # Рисуем игрока
    pygame.draw.circle(screen, (255, 0, 0), 
                       (player['x']*TILE_SIZE + TILE_SIZE//2, player['y']*TILE_SIZE + TILE_SIZE//2), 
                       TILE_SIZE//3)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()