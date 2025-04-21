# player.py
import pygame
from quest import Quest, KillQuest
from settings import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, INTERACTION_RANGE
from inventory import Inventory
from map import get_tile_at_position, collidable_tiles
from time import sleep

class Player:
    def __init__(self, x, y, time_system):
        self.image = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.base_speed = 200
        self.sprint_multiplier = 2.0
        self.time_system = time_system
        self.position = pygame.math.Vector2(x, y)
        self.health = 100
        self.max_health = 100
        self.stamina = 100
        self.max_stamina = 100
        self.stamina_drain_rate = 10
        self.stamina_recovery_rate = 1.11
        self.inventory = Inventory()
        self.interaction_prompt = {"text": "", "options": []}
        self.in_dialogue = False
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 0.5
        self.attack_damage = 10
        self.show_inventory = False
        self.show_quest_log = False
        self.interacting_npc = None
        self.quests = []
        
    def handle_input(self, dt, npcs, enemies, hud):
        keys = pygame.key.get_pressed()
        if self.show_inventory or self.show_quest_log:
            return
        if self.in_dialogue:
            try:
                if keys[pygame.K_e]:
                    self.interaction_prompt = self.interacting_npc.interact(self)
                    if not self.interaction_prompt["options"]:
                        self.in_dialogue = False
                        self.interacting_npc = None
                        self.interaction_prompt = {"text": "", "options": []}
                    sleep(0.2)
                elif keys[pygame.K_1] and self.interaction_prompt["options"]:
                    self.interacting_npc.handle_dialogue_option(self.interaction_prompt["options"][0]["action"], self, enemies, npcs)
                    self.interaction_prompt = self.interacting_npc.interact(self)
                    self.in_dialogue = False
                    self.interacting_npc = None
                    self.interaction_prompt = {"text": "", "options": []}
                    for quest in self.quests:
                        if quest.active and not quest.completed:
                            notification = quest.start()
                            hud.show_quest_modal(notification["name"], notification["description"], notification["status"])
                    sleep(0.2)
                elif keys[pygame.K_2] and self.interaction_prompt["options"]:
                    self.interacting_npc.handle_dialogue_option(self.interaction_prompt["options"][1]["action"], self, enemies, npcs)
                    self.interaction_prompt = self.interacting_npc.interact(self)
                    self.in_dialogue = False
                    self.interacting_npc = None
                    self.interaction_prompt = {"text": "", "options": []}
                    sleep(0.2)
            except Exception as e:
                print(f"Dialogue error: {e}")
                self.in_dialogue = False
                self.interacting_npc = None
                self.interaction_prompt = {"text": "", "options": []}
            return
        direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]: direction.y -= 1
        if keys[pygame.K_s]: direction.y += 1
        if keys[pygame.K_a]: direction.x -= 1
        if keys[pygame.K_d]: direction.x += 1
        is_sprinting = keys[pygame.K_LSHIFT] and self.stamina > 0
        speed = self.base_speed * self.sprint_multiplier if is_sprinting else self.base_speed
        if direction.length() > 0:
            direction.normalize_ip()
            new_position = self.position + direction * speed * dt
            new_rect = self.rect.copy()
            new_rect.center = round(new_position.x), round(new_position.y)
            corners = [
                (new_rect.left + 2, new_rect.top + 2),
                (new_rect.right - 2, new_rect.top + 2),
                (new_rect.left + 2, new_rect.bottom - 2),
                (new_rect.right - 2, new_rect.bottom - 2)
            ]
            collision = False
            for corner_x, corner_y in corners:
                tile = get_tile_at_position(corner_x, corner_y)
                if tile in collidable_tiles:
                    collision = True
                    break
            if not collision:
                self.position = new_position
                self.rect.center = round(self.position.x), round(self.position.y)
        # Update stamina
        if is_sprinting and direction.length() > 0:
            self.stamina = max(0, self.stamina - self.stamina_drain_rate * dt)
        elif self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_recovery_rate * dt)
        # Handle NPC interaction
        if keys[pygame.K_e]:
            for npc in npcs:
                distance = ((self.rect.centerx - npc.rect.centerx) ** 2 + (self.rect.centery - npc.rect.centery) ** 2) ** 0.5
                if distance < INTERACTION_RANGE:
                    if self.interacting_npc and self.interacting_npc != npc:
                        self.interacting_npc = None
                    self.interacting_npc = npc
                    self.in_dialogue = True
                    try:
                        self.interaction_prompt = npc.interact(self)
                        for quest in self.quests:
                            if isinstance(quest, Quest) and quest.active:
                                notification = quest.check_completion(self, npc, self.time_system)
                                if notification:
                                    hud.show_quest_modal(notification["name"], notification["description"], notification["status"])
                    except Exception as e:
                        print(f"Interaction error: {e}")
                        self.in_dialogue = False
                        self.interacting_npc = None
                        self.interaction_prompt = {"text": "", "options": []}
                    break
            sleep(0.2)
        # Handle attack
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if keys[pygame.K_SPACE] and self.attack_cooldown <= 0:
            for enemy in enemies:
                distance = ((self.rect.centerx - enemy.rect.centerx) ** 2 + (self.rect.centery - enemy.rect.centery) ** 2) ** 0.5
                if distance < INTERACTION_RANGE and enemy.alive:
                    enemy.take_damage(self.attack_damage)
                    self.attack_cooldown = self.attack_cooldown_duration
                    print(f"Attacked {enemy.name}, health: {enemy.health}")
                    for quest in self.quests:
                        if isinstance(quest, KillQuest):
                            notification = quest.check_completion(self, enemy, self.time_system)
                            if notification:
                                hud.show_quest_modal(notification["name"], notification["description"], notification["status"])
                    break
            for npc in npcs:
                distance = ((self.rect.centerx - npc.rect.centerx) ** 2 + (self.rect.centery - npc.rect.centery) ** 2) ** 0.5
                if distance < INTERACTION_RANGE and npc.alive:
                    npc.take_damage(self.attack_damage)
                    self.attack_cooldown = self.attack_cooldown_duration
                    print(f"Attacked {npc.name}, health: {npc.health}")
                    break
        if keys[pygame.K_1] and not self.in_dialogue:
            self.inventory.add_item("Potion")
            print("Added Potion")
            sleep(0.5)
        if keys[pygame.K_2] and not self.in_dialogue:
            self.inventory.remove_item("Potion")
            print("Removed Potion")
            sleep(0.5)
        if keys[pygame.K_c]:
            if "Potion" in self.inventory.items:
                self.inventory.remove_item("Potion")
                self.stamina = self.max_stamina
                print("Consumed Potion: Stamina restored to 100")
                sleep(0.25)
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        self.position.x, self.position.y = self.rect.center
        
    def update(self, dt, npcs, enemies, hud):
        self.handle_input(dt, npcs, enemies, hud)
        
    def draw_health_bar(self, surface, camera):
        bar_width = 30
        bar_height = 8
        health_ratio = self.health / self.max_health
        bar_x = self.rect.centerx - bar_width // 2 - camera.x
        bar_y = self.rect.top - 10 - camera.y
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def draw(self, surface, camera):
        surface.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
        self.draw_health_bar(surface, camera)