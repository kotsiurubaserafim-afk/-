import pygame
import socket
import json
import sys

USER_NAME = sys.argv[1] if len(sys.argv) > 1 else "Гравець"
TILE_SIZE = 40
VIEW_DIST = 3
pygame.init()
screen = pygame.display.set_mode((600, 520)) # Збільшили висоту для кнопки
font = pygame.font.SysFont("Arial", 16, bold=True)
clock = pygame.time.Clock()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5555))
client.send(json.dumps({"name": USER_NAME}).encode('utf-8'))

def exchange(data_dict):
    try:
        client.send(json.dumps(data_dict).encode('utf-8'))
        return json.loads(client.recv(8192).decode('utf-8'))
    except: return None

game_state = exchange({"dx": 0, "dy": 0})
running = True

while running:
    dx, dy = 0, 0
    btn_rect = pygame.Rect(200, 460, 200, 40) # Прямокутник кнопки

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: dy = -1
            elif event.key == pygame.K_DOWN: dy = 1
            elif event.key == pygame.K_LEFT: dx = -1
            elif event.key == pygame.K_RIGHT: dx = 1
            if dx != 0 or dy != 0: 
                game_state = exchange({"dx": dx, "dy": dy})
        
        # Обробка натискання кнопки мишкою
        if event.type == pygame.MOUSEBUTTONDOWN:
            if btn_rect.collidepoint(event.pos) and game_state and game_state['winners']:
                game_state = exchange({"type": "reset"})

    screen.fill((5, 5, 10))
    if game_state:
        my_id, players = game_state['id'], game_state['players']
        me = players[my_id]
        
        # Малювання лабіринту
        for y, row in enumerate(game_state['maze']):
            for x, cell in enumerate(row):
                if abs(x - me['x']) + abs(y - me['y']) <= VIEW_DIST:
                    rect = (x*TILE_SIZE, y*TILE_SIZE + 40, TILE_SIZE-1, TILE_SIZE-1)
                    colors = {1:(50,50,60), 2:(0,180,0), 3:(200,60,0), 4:(0,150,255), 0:(20,20,30)}
                    pygame.draw.rect(screen, colors.get(cell, (20,20,30)), rect)

        # Малювання гравців
        for p_id, p in players.items():
            if abs(p['x'] - me['x']) + abs(p['y'] - me['y']) <= VIEW_DIST:
                color = (0, 255, 100) if p_id == my_id else (255, 50, 50)
                px, py = p['x']*TILE_SIZE + 20, p['y']*TILE_SIZE + 60
                pygame.draw.circle(screen, color, (px, py), 15)
                screen.blit(font.render(p['name'], True, (255, 255, 255)), (px-20, py-35))

        # Таблиця переможців
        pygame.draw.rect(screen, (40, 40, 50), (0, 0, 600, 40))
        for i, name in enumerate(game_state['winners']):
            txt = font.render(f"{i+1} МІСЦЕ: {name}", True, (255, 215, 0))
            screen.blit(txt, (20 + i*180, 12))

        # КНОПКА ПЕРЕЗАПУСКУ (показуємо, якщо хтось виграв)
        if game_state['winners']:
            pygame.draw.rect(screen, (0, 100, 200), btn_rect)
            btn_txt = font.render("НОВА ГРА", True, (255, 255, 255))
            screen.blit(btn_txt, (btn_rect.centerx - 40, btn_rect.centery - 10))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()