# main.py
import pygame
import platform
import asyncio
import sys
from settings import *
from map import draw_map, draw_minimap, collidable_tiles
from player import Player
from camera import Camera
from npc import NPC
from hud import HUD
from enemy import Enemy
from time_system import TimeSystem
from weather import WeatherSystem
from menu import MainMenu
from pause_menu import PauseMenu

async def show_menu():
    menu = MainMenu()
    while True:
        result = menu.update()
        if result:
            if result["action"] == "start":
                return result
            elif result["action"] == "exit":
                pygame.quit()
                sys.exit()
            elif result["action"] == "settings":
                print("Settings opened")
        menu.draw()
        await asyncio.sleep(1.0 / FPS)
        
async def main():
    pygame.init()
    pygame.key.set_repeat(200, 200)  # 200ms delay for key repeat
    while True:
        # Show main menu
        menu_result = await show_menu()
        if menu_result["action"] != "start":
            return
        
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TopDown Pixel RPG")
        clock = pygame.time.Clock()
        
        # Initialize systems
        time_system = TimeSystem()
        time_system.set_time_scale(menu_result["time_scale"])
        player = Player(MAP_WIDTH // 2, MAP_HEIGHT // 2, time_system)
        camera = Camera(player)
        hud = HUD(player, time_system)
        npcs = [
            NPC(25 * TILE_SIZE, 45 * TILE_SIZE, "Villager1", "Welcome to our village!", time_system),
            NPC(65 * TILE_SIZE, 55 * TILE_SIZE, "Villager2", "The river is beautiful today.", time_system)
        ]
        enemies = [
            Enemy(25 * TILE_SIZE, 75 * TILE_SIZE, "Goblin1", (25 * TILE_SIZE, 45 * TILE_SIZE), time_system),
            Enemy(75 * TILE_SIZE, 25 * TILE_SIZE, "Goblin2", (65 * TILE_SIZE, 55 * TILE_SIZE), time_system),
            Enemy(30 * TILE_SIZE, 45 * TILE_SIZE, "Wolf1", (25 * TILE_SIZE, 45 * TILE_SIZE), time_system, "Wolf")
        ]
        # Lighting overlay
        lighting_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        lighting_surface.fill((50, 50, 50))
        weather_system = WeatherSystem(time_system)
        pause_menu = PauseMenu(screen)
        paused = False
        zoom_enabled = False
        mouse_clicked = False
        
        while True:
            dt = clock.tick(FPS) / 1000.0
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        paused = not paused
                        print(f"Paused: {paused}")
                    if event.key == pygame.K_i and not player.in_dialogue:
                        player.show_inventory = not player.show_inventory
                        print(f"Inventory toggled: {player.show_inventory}")
                    if event.key == pygame.K_t and not player.in_dialogue:
                        player.show_quest_log = not player.show_quest_log
                        print(f"Quest log toggled: {player.show_quest_log}")
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                    if not paused:
                        mouse_x, mouse_y = event.pos
                        minimap_rect = pygame.Rect(SCREEN_WIDTH - MINIMAP_SIZE - 10, 10, MINIMAP_SIZE, MINIMAP_SIZE)
                        if minimap_rect.collidepoint(mouse_x, mouse_y):
                            zoom_enabled = not zoom_enabled
            if paused:
                action = pause_menu.update(mouse_pos, mouse_clicked)
                if action == "continue":
                    paused = False
                    print(f"Paused: {paused}")
                elif action == "back":
                    break
            else:
                if not (player.show_inventory or player.show_quest_log):
                    player.update(dt, npcs, enemies, hud)
                    for enemy in enemies:
                        enemy.update(dt, player, collidable_tiles, time_system)
                    for npc in npcs:
                        npc.update(dt, time_system)
                    time_system.update(dt)
                    weather_system.update(dt)
                # Atualiza a câmera
                camera.update()
            # Desenha
            screen.fill((20, 20, 30))
            draw_map(screen, camera)
            for npc in npcs:
                npc.draw(screen, camera)
            for enemy in enemies:
                enemy.draw(screen, camera)
            player.draw(screen, camera)
            lighting_surface.set_alpha(time_system.get_lighting_alpha())
            screen.blit(lighting_surface, (0, 0))
            weather_system.draw(screen)
            draw_minimap(screen, camera, player, npcs, enemies, zoom_enabled)
            hud.draw(screen)
            if paused:
                pause_menu.draw()
            pygame.display.flip()
            mouse_clicked = False
            await asyncio.sleep(1.0 / FPS)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
