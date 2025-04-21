# menu.py
import pygame
import sys
import os
from settings import *

class MainMenu:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TopDown Pixel RPG - Main Menu")
        self.font = pygame.font.SysFont("arial", 30)
        self.background = pygame.image.load(os.path.join(os.path.dirname(__file__), "assets", "menu_background.png")).convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.buttons = [
            {"text": "Start", "rect": pygame.Rect(300, 200, 200, 50), "action": "start"},
            {"text": "Settings", "rect": pygame.Rect(300, 300, 200, 50), "action": "settings"},
            {"text": "Credits", "rect": pygame.Rect(300, 400, 200, 50), "action": "credits"},
            {"text": "Exit", "rect": pygame.Rect(300, 500, 200, 50), "action": "exit"}
        ]
        self.show_credits = False
        self.show_settings = False
        self.time_scale = 180  # Default: Fast (3 min/day)
        self.time_scales = [180, 1800, 10800]  # Fast, Medium, Normal
        self.settings_buttons = [
            {"text": f"Time: {self.get_time_label()}", "rect": pygame.Rect(300, 250, 200, 50), "action": "toggle_time"},
            {"text": "Back", "rect": pygame.Rect(300, 350, 200, 50), "action": "back"}
        ]
        self.back_button = {"text": "Back", "rect": pygame.Rect(300, 500, 200, 50), "action": "back"}
        self.clock = pygame.time.Clock()
        
    def get_time_label(self):
        if self.time_scale == 180:
            return "Fast (3 min/day)"
        elif self.time_scale == 1800:
            return "Medium (30 min/day)"
        return "Normal (3 hr/day)"

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"action": "exit"}
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        if self.show_credits:
            if self.back_button["rect"].collidepoint(mouse_pos) and mouse_clicked:
                self.show_credits = False
            return None
        
        if self.show_settings:
            for button in self.settings_buttons:
                if button["rect"].collidepoint(mouse_pos) and mouse_clicked:
                    if button["action"] == "toggle_time":
                        current_idx = self.time_scales.index(self.time_scale)
                        self.time_scale = self.time_scales[(current_idx + 1) % 3]
                        button["text"] = f"Time: {self.get_time_label()}"
                        print(f"Time scale set to: {self.time_scale} ({self.get_time_label()})")
                    elif button["action"] == "back":
                        self.show_settings = False
            return None

        for button in self.buttons:
            if button["rect"].collidepoint(mouse_pos) and mouse_clicked:
                if button["action"] == "credits":
                    self.show_credits = True
                elif button["action"] == "settings":
                    self.show_settings = True
                elif button["action"] == "start":
                    return {"action": "start", "time_scale": self.time_scale}
                else:
                    return {"action": button["action"]}
        return None

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        if self.show_credits:
            # Draw credits screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            credits_text = [
                "TopDown Pixel RPG",
                "Developed by Hyago",
                "Art: [Your Source]",
                "Music: [Your Source]",
                "Made with Pygame"
            ]
            for i, line in enumerate(credits_text):
                text_surface = self.font.render(line, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, 200 + i * 50))
                self.screen.blit(text_surface, text_rect)
            button = self.back_button
            color = (100, 100, 255) if button["rect"].collidepoint(pygame.mouse.get_pos()) else (50, 50, 200)
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
            text_surface = self.font.render(button["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button["rect"].center)
            self.screen.blit(text_surface, text_rect)
        elif self.show_settings:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            for button in self.settings_buttons:
                color = (100, 100, 255) if button["rect"].collidepoint(pygame.mouse.get_pos()) else (50, 50, 200)
                pygame.draw.rect(self.screen, color, button["rect"])
                pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
                text_surface = self.font.render(button["text"], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button["rect"].center)
                self.screen.blit(text_surface, text_rect)
        else:
            for button in self.buttons:
                color = (100, 100, 255) if button["rect"].collidepoint(pygame.mouse.get_pos()) else (50, 50, 200)
                pygame.draw.rect(self.screen, color, button["rect"])
                pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
                text_surface = self.font.render(button["text"], True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button["rect"].center)
                self.screen.blit(text_surface, text_rect)
        pygame.display.flip()