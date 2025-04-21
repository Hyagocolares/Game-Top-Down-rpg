# map.py
import pygame
from settings import TILE_SIZE, MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, MINIMAP_SIZE
import heapq

# Simulated chunk-based map (single 100x100 chunk for now)
CHUNK_SIZE = 50  # Tiles per chunk (for future expansion)
chunks = {(0, 0): []}  # Dictionary of chunks: (chunk_x, chunk_y) -> tile data

# Mapa 100x100 com rio, montanhas, ruas e vilarejos
map_data = []
for y in range(100):
    row = []
    for x in range(100):
        # Base de grama
        tile = 0
        # Rio diagonal (corta do canto superior esquerdo para inferior direito)
        if abs(x - y) < 3 and -1 < x < 100 and -1 < y < 100:
            tile = 2
        # Montanhas (região nordeste e sudoeste)
        if (x > 70 and y < 30) or (x < 30 and y > 70):
            if (x + y) % 7 < 4:
                tile = 1
        # Caverna nas montanhas sudoeste (3x3 área)
        if 23 <= x <= 27 and 73 <= y <= 77:
            tile = 5
        # Caverna nas montanhas nordeste (3x3 área)
        if 73 <= x <= 77 and 23 <= y <= 27:
            tile = 5 
        # Vilarejos (dois vilarejos com ruas)
        # Vilarejo 1 (centro-esquerda)
        if 20 < x < 30 and 45 < y < 55:
            tile = 3
            # Ruas no vilarejo 1
            if x == 25 or y == 50:
                tile = 4
        # Vilarejo 2 (centro-direita)
        if 60 < x < 70 and 45 < y < 55:
            tile = 3
            # Ruas no vilarejo 2
            if x == 65 or y == 50:
                tile = 4
        # Estrada principal conectando vilarejos
        if (y == 50 and 30 <= x <= 60) or (x == 45 and 50 <= y <= 60):
            tile = 4
        row.append(tile)
    map_data.append(row)
chunks[(0, 0)] = map_data

tile_colors = {
    0: (50, 200, 50),   # Grama
    1: (100, 100, 100), # Montanha
    2: (0, 150, 255),   # Rio
    3: (200, 150, 100), # Chão do vilarejo
    4: (150, 100, 50),  # Rua
    5: (50, 50, 50),    # Caverna
}

collidable_tiles = {1}

def get_neighbors(x, y, collidables):
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-directional movement
        nx, ny = x + dx, y + dy
        if 0 <= nx < 100 and 0 <= ny < 100:
            tile = chunks[(0, 0)][ny][nx]
            if tile not in collidables:
                neighbors.append((nx, ny))
    return neighbors

def find_nearest_bridge(start_x, start_y):
    bridge_tiles = []
    for x in range(30, 61):
        if chunks[(0, 0)][50][x] == 4:
            bridge_tiles.append((x, 50))
    for y in range(50, 61):
        if chunks[(0, 0)][y][45] == 4:
            bridge_tiles.append((45, y))
    if not bridge_tiles:
        return None
    closest_bridge = min(
        bridge_tiles,
        key=lambda b: (b[0] - start_x) ** 2 + (b[1] - start_y) ** 2
    )
    return closest_bridge

def find_path_to_tile(start_x, start_y, goal_x, goal_y, collidables):
    open_set = [(0, (start_x, start_y))]
    came_from = {}
    g_score = {(start_x, start_y): 0}
    f_score = {(start_x, start_y): abs(goal_x - start_x) + abs(goal_y - start_y)}
    while open_set:
        current_f, current = heapq.heappop(open_set)
        if current == (goal_x, goal_y):
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]
        for neighbor in get_neighbors(*current, collidables):
            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + abs(neighbor[0] - goal_x) + abs(neighbor[1] - goal_y)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []  # No path found

def draw_map(surface, camera):
    start_x = max(0, int(camera.x // TILE_SIZE))
    end_x = min(100, start_x + (SCREEN_WIDTH // TILE_SIZE) + 2)
    start_y = max(0, int(camera.y // TILE_SIZE))
    end_y = min(100, start_y + (SCREEN_HEIGHT // TILE_SIZE) + 2)
    chunk = chunks[(0, 0)]
    for y in range(start_y, end_y):
        for x in range(start_x, end_x):
            tile = chunk[y][x]
            color = tile_colors.get(tile, (255, 0, 0))
            rect = pygame.Rect(x * TILE_SIZE - camera.x, y * TILE_SIZE - camera.y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (min(color[0]+20, 255), min(color[1]+20, 255), min(color[2]+20, 255)), rect, 1)
            
def draw_minimap(surface, camera, player, npcs, enemies, zoom_enabled):
    minimap_surface = pygame.Surface((MINIMAP_SIZE, MINIMAP_SIZE))
    minimap_surface.fill((20, 20, 30))
    chunk = chunks[(0, 0)]
    map_tiles = 100
    if zoom_enabled:
        tile_scale = 4.0
        tiles_visible = MINIMAP_SIZE / tile_scale
        player_tile_x = player.rect.centerx / TILE_SIZE
        player_tile_y = player.rect.centery / TILE_SIZE
        start_x = max(0, int(player_tile_x - tiles_visible / 2))
        start_y = max(0, int(player_tile_y - tiles_visible / 2))
        start_x = max(0, min(len(chunk[0]) - int(tiles_visible), start_x))
        start_y = max(0, min(len(chunk) - int(tiles_visible), start_y))
        end_x = min(map_tiles, start_x + int(tiles_visible))
        end_y = min(map_tiles, start_y + int(tiles_visible))
        offset_x = MINIMAP_SIZE / 2 - (player_tile_x - start_x) * tile_scale
        offset_y = MINIMAP_SIZE / 2 - (player_tile_y - start_y) * tile_scale
    else:
        tile_scale = 2.0
        start_x = 0
        start_y = 0
        end_x = map_tiles
        end_y = map_tiles
        offset_x = 0
        offset_y = 0
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile = chunk[y][x]
                color = tile_colors.get(tile, (255, 0, 0))
                rect = pygame.Rect(
                    offset_x + (x - start_x) * tile_scale,
                    offset_y + (y - start_y) * tile_scale,
                    tile_scale,
                    tile_scale
                )
                if 0 <= rect.x < MINIMAP_SIZE and 0 <= rect.y < MINIMAP_SIZE:
                    pygame.draw.rect(minimap_surface, color, rect)
        # Draw NPCs
        for npc in npcs:
            tile_x = npc.rect.centerx / TILE_SIZE
            tile_y = npc.rect.centery / TILE_SIZE
            if start_x <= tile_x < end_x and start_y <= tile_y < end_y:
                minimap_x = offset_x + (tile_x - start_x) * tile_scale
                minimap_y = offset_y + (tile_y - start_y) * tile_scale
                if 0 <= minimap_x < MINIMAP_SIZE and 0 <= minimap_y < MINIMAP_SIZE:
                    pygame.draw.circle(minimap_surface, (255, 0, 255), (int(minimap_x), int(minimap_y)), 3)
        # Draw enemies
        for enemy in enemies:
            if enemy.alive and enemy.visible:
                tile_x = enemy.rect.centerx / TILE_SIZE
                tile_y = enemy.rect.centery / TILE_SIZE
                if start_x <= tile_x < end_x and start_y <= tile_y < end_y:
                    minimap_x = offset_x + (tile_x - start_x) * tile_scale
                    minimap_y = offset_y + (tile_y - start_y) * tile_scale
                    if 0 <= minimap_x < MINIMAP_SIZE and 0 <= minimap_y < MINIMAP_SIZE:
                        pygame.draw.circle(minimap_surface, (255, 0, 0), (int(minimap_x), int(minimap_y)), 3)
        # Draw player
        tile_x = player.rect.centerx / TILE_SIZE
        tile_y = player.rect.centery / TILE_SIZE
        if start_x <= tile_x < end_x and start_y <= tile_y < end_y:
            minimap_x = offset_x + (tile_x - start_x) * tile_scale
            minimap_y = offset_y + (tile_y - start_y) * tile_scale
            if 0 <= minimap_x < MINIMAP_SIZE and 0 <= minimap_y < MINIMAP_SIZE:
                pygame.draw.circle(minimap_surface, (255, 255, 0), (int(minimap_x), int(minimap_y)), 3)
    # Draw border
    pygame.draw.rect(minimap_surface, (200, 200, 200), (0, 0, MINIMAP_SIZE, MINIMAP_SIZE), 2)
    surface.blit(minimap_surface, (SCREEN_WIDTH - MINIMAP_SIZE - 10, 10))
    # Debug minimap click
    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if SCREEN_WIDTH - MINIMAP_SIZE - 10 <= mouse_x < SCREEN_WIDTH - 10 and 10 <= mouse_y < 10 + MINIMAP_SIZE:
            print(f"Minimap clicked. Player: ({tile_x:.1f}, {tile_y:.1f}) -> ({minimap_x:.1f}, {minimap_y:.1f})")

def get_tile_at_position(x, y):
    chunk = chunks.get((0, 0), None)
    if not chunk:
        return None
    tile_x = int(x // TILE_SIZE)
    tile_y = int(y // TILE_SIZE)
    if 0 <= tile_y < 100 and 0 <= tile_x < 100:
        return chunk[tile_y][tile_x]
    return None
