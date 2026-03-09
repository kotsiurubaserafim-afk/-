import pygame
import os

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("Реєстрація гравця")
font = pygame.font.SysFont("Arial", 24)
color_inactive = pygame.Color('lightskyblue3')
color_active = pygame.Color('dodgerblue2')
color = color_inactive

active = False
text = ''
running = True

while running:
    screen.fill((30, 30, 30))
    # Малюємо підказку
    prompt = font.render("Введіть ваше ім'я та натисніть Enter:", True, (255, 255, 255))
    screen.blit(prompt, (50, 80))

    # Поле вводу
    txt_surface = font.render(text, True, (255, 255, 255))
    width = max(200, txt_surface.get_width()+10)
    input_rect = pygame.Rect(100, 130, width, 40)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            active = input_rect.collidepoint(event.pos)
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    if text.strip():
                        # Запускаємо клієнт з передачею імені як аргумента
                        os.system(f"python client.py {text}")
                        running = False
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    pygame.draw.rect(screen, color, input_rect, 2)
    screen.blit(txt_surface, (input_rect.x+5, input_rect.y+5))
    pygame.display.flip()

pygame.quit()