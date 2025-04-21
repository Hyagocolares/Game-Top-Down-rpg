# npc.py
import pygame
from quest import KillQuest, Quest
from settings import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT

class NPC:
    def __init__(self, x, y, name, dialogue, time_system):
        self.image = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.name = name
        self.health = 100
        self.max_health = 100
        self.alive = True
        self.time_system = time_system
        self.base_position = pygame.math.Vector2(x, y)
        self.schedule = [
            (6, 12, self.base_position),  # Morning: Stay at base
            (12, 18, pygame.math.Vector2(30 * TILE_SIZE, 50 * TILE_SIZE)),  # Afternoon: Move to river
            (18, 6, self.base_position)  # Night: Return to base
        ]
        self.speed = 100
        self.quest_data = {
            "Villager1": {
                "prologue": f"{name}: A wolf has been attacking our livestock at night!",
                "quest_dialogue": "Can you kill the wolf that appears at night (21:00-5:59)?",
                "quest_type": "KillQuest",
                "quest_params": {
                    "name": "Kill Wolf",
                    "description": "Kill Wolf1 at night (21:00-5:59).",
                    "start_hour": 21,
                    "end_hour": 6,
                    "reward": "Sword"
                }
            },
            "Villager2": {
                "prologue": f"{name}: I need to send an urgent message to Villager1.",
                "quest_dialogue": "Can you deliver this message to Villager1 before night (21:00)?",
                "quest_type": "Quest",
                "quest_params": {
                    "name": "Deliver Message",
                    "description": "Deliver to Villager1 before night.",
                    "deadline_hour": 21,
                    "reward": "Potion"
                }
            }
        }.get(name, {})
        self.dialogue = dialogue
        self.current_dialogue = "greeting"
        self.quest_status = "none"  # none, offered, accepted, declined, failed, completed
        self.dialogue_tree = {
            "greeting": {
                "text": dialogue,
                "next": "prologue" if self.quest_data else None
            },
            "prologue": {
                "text": self.quest_data.get("prologue", dialogue),
                "next": "quest_offer" if self.quest_data else None
            },
            "quest_offer": {
                "text": self.quest_data.get("quest_dialogue", dialogue),
                "options": [
                    {"text": "Accept", "key": pygame.K_1, "action": "accept_quest"},
                    {"text": "Decline", "key": pygame.K_2, "action": "decline_quest"}
                ]
            },
            "declined": {
                "text": f"{name}: Maybe another time.",
                "next": None
            },
            "completed": {
                "text": f"{name}: You did it! Thank you!",
                "next": None
            },
            "failed": {
                "text": f"{name}: Oh no, we missed our chance!",
                "next": None
            }
        }
        self.last_quest_day = 0

    def draw(self, surface, camera):
        if self.alive:
            surface.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
            if self.health < self.max_health:
                self.draw_health_bar(surface, camera)

    def draw_health_bar(self, surface, camera):
        bar_width = 30
        bar_height = 8
        health_ratio = self.health / self.max_health
        bar_x = self.rect.centerx - bar_width // 2 - camera.x
        bar_y = self.rect.top - 10 - camera.y
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (200, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    def interact(self, player):
        if not self.alive:
            return {"text": f"{self.name} is dead.", "options": []}
        if self.quest_status in ["completed", "failed"] and self.time_system.day > self.last_quest_day:
            self.reset_quest_state()
        if self.quest_status in ["accepted", "completed", "failed", "declined"]:
            return {"text": self.dialogue, "options": []}
        current_node = self.dialogue_tree.get(self.current_dialogue, {"text": self.dialogue, "options": []})
        if current_node.get("options"):
            self.quest_status = "offered"
            return {"text": current_node["text"], "options": current_node["options"]}
        if current_node.get("next"):
            self.current_dialogue = current_node["next"]
            next_node = self.dialogue_tree[self.current_dialogue]
            if next_node.get("options"):
                self.quest_status = "offered"
            return {"text": next_node["text"], "options": next_node.get("options", [])}
        return {"text": current_node["text"], "options": []}
    
    def handle_dialogue_option(self, action, player, enemies, npcs):
        if action == "accept_quest" and self.quest_status == "offered":
            quest_info = self.quest_data
            if quest_info["quest_type"] == "Quest":
                quest = Quest(
                    quest_info["quest_params"]["name"],
                    quest_info["quest_params"]["description"],
                    npcs[0] if self.name == "Villager2" else None,
                    quest_info["quest_params"]["deadline_hour"],
                    quest_info["quest_params"]["reward"],
                    self
                )
            elif quest_info["quest_type"] == "KillQuest":
                quest = KillQuest(
                    quest_info["quest_params"]["name"],
                    quest_info["quest_params"]["description"],
                    enemies[2] if self.name == "Villager1" else None,
                    quest_info["quest_params"]["start_hour"],
                    quest_info["quest_params"]["end_hour"],
                    quest_info["quest_params"]["reward"],
                    self
                )
            quest.start()
            player.quests.append(quest)
            self.quest_status = "accepted"
            self.current_dialogue = "greeting"
            print(f"Quest accepted: {quest.name}")
        elif action == "decline_quest":
            self.quest_status = "declined"
            self.current_dialogue = "declined"
            print(f"Quest declined from {self.name}")
    
    def reset_quest_state(self):
        self.quest_status = "none"
        self.current_dialogue = "greeting"
        self.last_quest_day = self.time_system.day

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        if self.health <= 0:
            self.alive = False
            print(f"{self.name} killed")

    def update(self, dt, time_system):
        if not self.alive:
            return
        hour = time_system.hour
        if 6 <= hour < 12:
            self.dialogue = f"{self.name}: Good morning!"
        elif 12 <= hour < 18:
            self.dialogue = f"{self.name}: Good afternoon!"
        else:
            self.dialogue = f"{self.name}: Good night!"
        for start, end, pos in self.schedule:
            if (start <= hour < end) or (end < start and (hour >= start or hour < end)):
                direction = pos - pygame.math.Vector2(self.rect.center)
                if direction.length() > 5:
                    direction.normalize_ip()
                    new_pos = pygame.math.Vector2(self.rect.center) + direction * self.speed * dt
                    self.rect.center = round(new_pos.x), round(new_pos.y)
                break
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))