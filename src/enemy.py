# enemy.py
import pygame
import random
import math
from settings import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT
from map import get_tile_at_position, find_nearest_bridge, find_path_to_tile

class Enemy:
    def __init__(self, x, y, name, village_position, time_system, enemy_type="Goblin"):
        self.image = pygame.Surface((TILE_SIZE-4, TILE_SIZE-4))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
        self.name = name
        self.time_system = time_system
        self.enemy_type = enemy_type
        self.max_health = 30 if enemy_type == "Wolf" else 50
        self.health = self.max_health
        self.alive = True
        self.speed = 200 if enemy_type == "Wolf" else 150
        self.spawn_hour = 21 if enemy_type == "Wolf" else None
        self.despawn_hour = 6 if enemy_type == "Wolf" else None
        self.visible = enemy_type != "Wolf"
        self.detection_range = 200
        self.base_position = pygame.math.Vector2(x, y)
        self.village_position = pygame.math.Vector2(village_position)
        self.patrol_radius = 96
        self.patrol_angle = random.uniform(0, 2 * 3.14159)
        self.patrol_speed = 0.5
        self.state = "Patrol"
        self.state_timer = 0
        self.chase_duration = 3.0
        self.damage = 5
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 1.0
        self.path = []
    
    def update(self, dt, player, map_collidables, time_system):
        if self.enemy_type == "Wolf":
            if time_system.hour == 6 and self.visible:
                self.visible = False
                self.state = "Patrol"
                self.path = []
                self.patrol_angle = random.uniform(0, 2 * 3.14159)
                print(f"{self.name} despawned at 6:00")
            else:
                self.visible = time_system.hour in [21, 22, 23, 0, 1, 2, 3, 4, 5]
        if not self.alive or not self.visible:
            return
        
        # Update timers
        self.state_timer -= dt
        self.attack_cooldown -= dt
        
        # Calculate distance to player
        player_distance = ((self.rect.centerx - player.rect.centerx) ** 2 + (self.rect.centery - player.rect.centery) ** 2) ** 0.5
        
        # State transitions
        if player_distance < self.detection_range and self.state != "Chase":
            self.state = "Chase"
            self.state_timer = self.chase_duration
            self.path = []
        elif self.state == "Chase" and player_distance >= self.detection_range and self.state_timer <= 0:
            self.state = "Return"
            self.path = []
        elif self.state == "Patrol" and time_system.hour in [21, 22, 23, 0, 1, 2, 3, 4, 5]:
            self.state = "ToVillage"
            self.path = []
        elif self.state == "ToVillage":
            village_distance = (pygame.math.Vector2(self.rect.center) - self.village_position).length()
            if village_distance < 10:
                self.state = "VillagePatrol"
                self.patrol_angle = random.uniform(0, 2 * 3.14159)
                self.path = []
        elif self.state == "VillagePatrol" and time_system.hour not in [21, 22, 23, 0, 1, 2, 3, 4, 5]:
            self.state = "Return"
            self.path = []
        elif self.state == "Return":
            return_distance = (pygame.math.Vector2(self.rect.center) - self.base_position).length()
            if return_distance < 10:
                self.state = "Patrol"
                self.patrol_angle = random.uniform(0, 2 * 3.14159)
                self.path = []
                
        # Movement logic
        direction = pygame.math.Vector2(0, 0)
        speed = self.speed
        if self.state == "Chase":
            self_tile_x, self_tile_y = self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE
            player_tile_x, player_tile_y = player.rect.centerx // TILE_SIZE, player.rect.centery // TILE_SIZE
            self_on_river = get_tile_at_position(self.rect.centerx, self.rect.centery) == 2
            player_on_river = get_tile_at_position(player.rect.centerx, player.rect.centery) == 2
            river_between = abs(self_tile_x - player_tile_x) < 3 and 20 < self_tile_x < 80 and 20 < player_tile_y < 80
            
            if river_between and not (self_on_river or player_on_river):
                if not self.path:
                    bridge_tile = find_nearest_bridge(self_tile_x, self_tile_y)
                    if bridge_tile:
                        self.path = find_path_to_tile(self_tile_x, self_tile_y, bridge_tile[0], bridge_tile[1], map_collidables)
                if self.path:
                    next_tile_x, next_tile_y = self.path[0]
                    direction = pygame.math.Vector2(
                        (next_tile_x * TILE_SIZE + TILE_SIZE // 2) - self.rect.centerx,
                        (next_tile_y * TILE_SIZE + TILE_SIZE // 2) - self.rect.centery
                    )
                    if direction.length() > 0:
                        direction.normalize_ip()
                    if direction.length() < 5:
                        self.path.pop(0)
            else:
                direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                if direction.length() > 0:
                    direction.normalize_ip()
        elif self.state == "Patrol":
            self.patrol_angle += self.patrol_speed * dt * random.choice([1, -1])
            target_pos = self.base_position + pygame.math.Vector2(
                self.patrol_radius * math.cos(self.patrol_angle),
                self.patrol_radius * math.sin(self.patrol_angle)
            )
            direction = target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                direction.normalize_ip()
            speed = self.speed * 0.5
        elif self.state == "VillagePatrol":
            self.patrol_angle += self.patrol_speed * dt * random.choice([1, -1])
            target_pos = self.village_position + pygame.math.Vector2(
                self.patrol_radius * math.cos(self.patrol_angle),
                self.patrol_radius * math.sin(self.patrol_angle)
            )
            direction = target_pos - pygame.math.Vector2(self.rect.center)
            if direction.length() > 0:
                direction.normalize_ip()
            speed = self.speed * 0.5
        elif self.state == "ToVillage":
            self_tile_x, self_tile_y = self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE
            village_tile_x, village_tile_y = int(self.village_position.x // TILE_SIZE), int(self.village_position.y // TILE_SIZE)
            self_on_river = get_tile_at_position(self.rect.centerx, self.rect.centery) == 2
            village_on_river = get_tile_at_position(self.village_position.x, self.village_position.y) == 2
            river_between = abs(self_tile_x - village_tile_x) < 3 and 20 < self_tile_x < 80 and 20 < village_tile_y < 80
            if river_between and not (self_on_river or village_on_river):
                if not self.path:
                    bridge_tile = find_nearest_bridge(self_tile_x, self_tile_y)
                    if bridge_tile:
                        self.path = find_path_to_tile(self_tile_x, self_tile_y, bridge_tile[0], bridge_tile[1], map_collidables)
                if self.path:
                    next_tile_x, next_tile_y = self.path[0]
                    direction = pygame.math.Vector2(
                        (next_tile_x * TILE_SIZE + TILE_SIZE // 2) - self.rect.centerx,
                        (next_tile_y * TILE_SIZE + TILE_SIZE // 2) - self.rect.centery
                    )
                    if direction.length() > 0:
                        direction.normalize_ip()
                    if direction.length() < 5:
                        self.path.pop(0)
            else:
                if not self.path:
                    self.path = find_path_to_tile(self_tile_x, self_tile_y, village_tile_x, village_tile_y, map_collidables)
                if self.path:
                    next_tile_x, next_tile_y = self.path[0]
                    direction = pygame.math.Vector2(
                        (next_tile_x * TILE_SIZE + TILE_SIZE // 2) - self.rect.centerx,
                        (next_tile_y * TILE_SIZE + TILE_SIZE // 2) - self.rect.centery
                    )
                    if direction.length() > 0:
                        direction.normalize_ip()
                    if direction.length() < 5:
                        self.path.pop(0)
                else:
                    direction = self.village_position - pygame.math.Vector2(self.rect.center)
                    if direction.length() > 0:
                        direction.normalize_ip()
            speed = self.speed
        elif self.state == "Return":
            if not self.path:
                self_tile_x, self_tile_y = self.rect.centerx // TILE_SIZE, self.rect.centery // TILE_SIZE
                base_tile_x, base_tile_y = int(self.base_position.x // TILE_SIZE), int(self.base_position.y // TILE_SIZE)
                self.path = find_path_to_tile(self_tile_x, self_tile_y, base_tile_x, base_tile_y, map_collidables)
            if self.path:
                next_tile_x, next_tile_y = self.path[0]
                direction = pygame.math.Vector2(
                    (next_tile_x * TILE_SIZE + TILE_SIZE // 2) - self.rect.centerx,
                    (next_tile_y * TILE_SIZE + TILE_SIZE // 2) - self.rect.centery
                )
                if direction.length() > 0:
                    direction.normalize_ip()
                if direction.length() < 5:
                    self.path.pop(0)
            else:
                direction = self.base_position - pygame.math.Vector2(self.rect.center)
                if direction.length() > 0:
                    direction.normalize_ip()
            speed = self.speed * 1.5
        new_position = pygame.math.Vector2(self.rect.center) + direction * speed * dt
        new_rect = self.rect.copy()
        new_rect.center = round(new_position.x), round(new_position.y)
        # Collision check
        corners = [
            (new_rect.left + 2, new_rect.top + 2),
            (new_rect.right - 2, new_rect.top + 2),
            (new_rect.left + 2, new_rect.bottom - 2),
            (new_rect.right - 2, new_rect.bottom - 2)
        ]
        collision = False
        for corner_x, corner_y in corners:
            tile = get_tile_at_position(corner_x, corner_y)
            if tile in map_collidables:
                collision = True
                break
        if not collision:
            self.rect.center = new_rect.center
        # Clamp to map boundaries
        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        # Attack player on contact
        if self.rect.colliderect(player.rect) and self.attack_cooldown <= 0:
            player.health = max(0, player.health - self.damage)
            self.attack_cooldown = self.attack_cooldown_duration
            print(f"{self.name} attacked player, player health: {player.health}")

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            print(f"{self.name} killed")

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
        if self.alive and self.visible:
            surface.blit(self.image, (self.rect.x - camera.x, self.rect.y - camera.y))
            self.draw_health_bar(surface, camera)