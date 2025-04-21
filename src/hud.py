# hud.py
import pygame
from settings import FPS, SCREEN_WIDTH, SCREEN_HEIGHT

class HUD:
    def __init__(self, player, time_system):
        self.player = player
        self.time_system = time_system
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)
        self.dialogue_alpha = 0
        self.fade_timer = 0
        self.fade_duration = 0.5
        self.quest_modal = None
        self.quest_modal_alpha = 0
        self.quest_modal_timer = 0
        self.quest_modal_duration = 3.0
        self.quest_fade_duration = 0.5

    def wrap_text(self, text, max_width, font):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            width = font.render(test_line, True, (255, 255, 255)).get_width()
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        return lines

    def show_quest_modal(self, name, description, status):
        self.quest_modal = {
            "name": name,
            "description": description,
            "status": status,
            "timer": 0,
            "alpha": 0
        }
        self.quest_modal_timer = 0
    
    def draw(self, surface):
        # Draw time display (top center)
        time_text = self.font.render(self.time_system.get_time_string(), True, (255, 255, 255))
        time_box_width, time_box_height = 200, 30
        time_box_surface = pygame.Surface((time_box_width, time_box_height), pygame.SRCALPHA)
        time_box_surface.fill((0, 0, 0, 180))  # Semi-transparent black
        pygame.draw.rect(time_box_surface, (255, 255, 255), (0, 0, time_box_width, time_box_height), 2)  # White border
        text_rect = time_text.get_rect(center=(time_box_width // 2, time_box_height // 2))
        time_box_surface.blit(time_text, text_rect)
        surface.blit(time_box_surface, (SCREEN_WIDTH // 2 - time_box_width // 2, 10))
        # Draw health
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        surface.blit(health_text, (10, SCREEN_HEIGHT - 50))
        # Draw stamina bar
        stamina_bar_width = 100
        stamina_bar_height = 10
        stamina_ratio = self.player.stamina / self.player.max_stamina
        pygame.draw.rect(surface, (50, 50, 50), (10, SCREEN_HEIGHT - 70, stamina_bar_width, stamina_bar_height))  # Background
        pygame.draw.rect(surface, (0, 200, 0), (10, SCREEN_HEIGHT - 70, stamina_bar_width * stamina_ratio, stamina_bar_height))  # Filled
        pygame.draw.rect(surface, (255, 255, 255), (10, SCREEN_HEIGHT - 70, stamina_bar_width, stamina_bar_height), 1)  # Border
        # Draw inventory
        inventory_text = self.font.render(f"Items: {', '.join(self.player.inventory.items) or 'None'}", True, (255, 255, 255))
        surface.blit(inventory_text, (10, SCREEN_HEIGHT - 30))
        # Draw interaction prompt
        if self.player.interaction_prompt["text"]:
            if self.fade_timer < self.fade_duration:
                self.fade_timer += 1 / FPS
                self.dialogue_alpha = (self.fade_timer / self.fade_duration) * 180
            else:
                self.dialogue_alpha = 180
            # Create dialogue box surface
            box_width, box_height = 500, 120
            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 0, int(self.dialogue_alpha)))
            pygame.draw.rect(box_surface, (255, 255, 255), (0, 0, box_width, box_height), 2)
            if self.player.interacting_npc:
                npc_name = self.font.render(self.player.interacting_npc.name, True, (255, 255, 255))
                box_surface.blit(npc_name, (10, 10))
            lines = self.wrap_text(self.player.interaction_prompt["text"], 450, self.font)
            for i, line in enumerate(lines[:3]):  # Limit to 3 lines
                text_surface = self.font.render(line, True, (255, 255, 255))
                box_surface.blit(text_surface, (10, 30 + i * 20))
            if self.player.interaction_prompt["options"]:
                options_text = "  ".join(f"{i+1}. {opt['text']}" for i, opt in enumerate(self.player.interaction_prompt["options"]))
                options_surface = self.font.render(options_text, True, (255, 255, 255))
                box_surface.blit(options_surface, (10, 90))
            surface.blit(box_surface, (SCREEN_WIDTH // 2 - box_width // 2, SCREEN_HEIGHT - box_height - 10))
        else:
            if self.fade_timer > 0:
                self.fade_timer -= 1 / FPS
                self.dialogue_alpha = (self.fade_timer / self.fade_duration) * 180
            else:
                self.dialogue_alpha = 0
        if self.quest_modal:
            self.quest_modal_timer += 1 / FPS
            if self.quest_modal_timer < self.quest_fade_duration:
                self.quest_modal_alpha = (self.quest_modal_timer / self.quest_fade_duration) * 180
            elif self.quest_modal_timer < self.quest_modal_duration - self.quest_fade_duration:
                self.quest_modal_alpha = 180
            else:
                self.quest_modal_alpha = ((self.quest_modal_duration - self.quest_modal_timer) / self.quest_fade_duration) * 180
            if self.quest_modal_timer >= self.quest_modal_duration:
                self.quest_modal = None
                self.quest_modal_alpha = 0
                self.quest_modal_timer = 0
            else:
                box_width, box_height = 400, 100
                box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                box_surface.fill((0, 0, 0, int(self.quest_modal_alpha)))
                pygame.draw.rect(box_surface, (255, 255, 255), (0, 0, box_width, box_height), 2)
                name_text = self.font.render(self.quest_modal["name"], True, (255, 255, 255))
                box_surface.blit(name_text, (10, 20))
                lines = self.wrap_text(self.quest_modal["description"], 280, self.small_font)
                for i, line in enumerate(lines[:2]):
                    desc_text = self.small_font.render(line, True, (255, 255, 255))
                    box_surface.blit(desc_text, (10, 40 + i * 20))
                status_text = self.small_font.render(self.quest_modal["status"], True, (255, 255, 255))
                box_surface.blit(status_text, (10, 80))
                surface.blit(box_surface, (SCREEN_WIDTH - box_width - box_width, 50))
        # Draw inventory panel
        if self.player.show_inventory:
            box_width, box_height = 300, 200
            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 0, 180))
            pygame.draw.rect(box_surface, (255, 255, 255), (0, 0, box_width, box_height), 2)
            # Title
            title_text = self.font.render("Inventory", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(box_width // 2, 20))
            box_surface.blit(title_text, title_rect)
            # Items
            if self.player.inventory.items:
                for i, item in enumerate(self.player.inventory.items):
                    item_text = self.font.render(item, True, (255, 255, 255))
                    item_rect = item_text.get_rect(center=(box_width // 2, 50 + i * 30))
                    box_surface.blit(item_text, item_rect)
            else:
                empty_text = self.font.render("Empty", True, (255, 255, 255))
                empty_rect = empty_text.get_rect(center=(box_width // 2, 50))
                box_surface.blit(empty_text, empty_rect)
            surface.blit(box_surface, (SCREEN_WIDTH // 2 - box_width // 2, SCREEN_HEIGHT // 2 - box_height // 2))
        # Draw quest panel
        if self.player.show_quest_log:
            box_width, box_height = 300, 200
            box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surface.fill((0, 0, 0, 180))
            pygame.draw.rect(box_surface, (255, 255, 255), (0, 0, box_width, box_height), 2)
            title_text = self.font.render("Quest Log", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(box_width // 2, 20))
            box_surface.blit(title_text, title_rect)
            if self.player.quests:
                for i, quest in enumerate(self.player.quests):
                    if i * 30 + 50 > box_height - 20:
                        break
                    quest_text = self.font.render(f"{quest.name}: {quest.get_progress()}", True, (255, 255, 255))
                    quest_rect = quest_text.get_rect(center=(box_width // 2, 50 + i * 30))
                    box_surface.blit(quest_text, quest_rect)
                    time_text = self.font.render(quest.get_time_info(), True, (255, 255, 255))
                    time_rect = time_text.get_rect(center=(box_width // 2, 80 + i * 30))
                    box_surface.blit(time_text, time_rect)
            else:
                empty_text = self.font.render("No active quests", True, (255, 255, 255))
                empty_rect = empty_text.get_rect(center=(box_width // 2, 50))
                box_surface.blit(empty_text, empty_rect)
            surface.blit(box_surface, (SCREEN_WIDTH // 2 - box_width // 2, SCREEN_HEIGHT // 2 - box_height // 2))