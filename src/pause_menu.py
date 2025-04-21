# pause_menu.py
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 30)
        self.buttons = [
            {"text": "Continue", "rect": pygame.Rect(300, 250, 200, 50), "action": "continue"},
            {"text": "Back", "rect": pygame.Rect(300, 350, 200, 50), "action": "back"}
        ]

    def update(self, mouse_pos, mouse_clicked):
        if mouse_clicked:
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    print(f"Button clicked: {button['text']}")
                    return button["action"]
        return None

    def draw(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        print("Drawing pause menu")
        for button in self.buttons:
            color = (100, 100, 255) if button["rect"].collidepoint(pygame.mouse.get_pos()) else (50, 50, 200)
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
            text_surface = self.font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button["rect"].center)
            self.screen.blit(text_surface, text_rect)
            print(f"Drawing button: {button['text']} at {button['rect']}")