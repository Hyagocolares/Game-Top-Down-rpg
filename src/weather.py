# weather.py
import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class WeatherSystem:
    def __init__(self, time_system):
        self.time_system = time_system
        self.weather_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.rain_particles = []
        self.snow_particles = []
        self.fog_particles = []
        self.weather_type = "clear"  # clear, rain, snow, fog
        self.weather_alpha = 0  # Current alpha (0–100)
        self.target_alpha = 0  # Target alpha for fade
        self.fade_duration = 10.0  # Fade over 10 seconds
        self.fade_timer = 0
        self.max_particles = {"rain": 200, "snow": 100, "fog": 50}
        self.is_fading_out = False  # Track fade-out state

    def get_weather_for_hour(self, hour):
        if hour in [21, 22, 23, 3, 4, 5]:
            return "rain"
        elif hour in [0, 1, 2]:
            return "snow"
        elif hour in [19, 20]:
            return "fog"
        return "clear"
    
    def update(self, dt):
        hour = self.time_system.hour
        new_weather = self.get_weather_for_hour(hour)

        # Handle weather transition
        if new_weather != self.weather_type:
            self.weather_type = new_weather
            self.fade_timer = 0
            self.is_fading_out = (new_weather == "clear")
            self.target_alpha = 100 if new_weather != "clear" else 0
            if new_weather == "clear":
                # Don't clear particles immediately; let them fade out
                pass
            else:
                # Clear particles for new weather type
                self.rain_particles = []
                self.snow_particles = []
                self.fog_particles = []

        # Update fade
        if self.fade_timer < self.fade_duration:
            self.fade_timer += dt
            progress = min(self.fade_timer / self.fade_duration, 1.0)
            if self.is_fading_out:
                # Fade out: from current alpha to 0
                self.weather_alpha = int((1 - progress) * self.weather_alpha)
            else:
                # Fade in: from 0 to target_alpha
                self.weather_alpha = int(progress * self.target_alpha)
        else:
            self.weather_alpha = self.target_alpha
            self.is_fading_out = False

        # Clear off-screen particles
        self.rain_particles = [p for p in self.rain_particles if p[1] < SCREEN_HEIGHT]
        self.snow_particles = [p for p in self.snow_particles if p[1] < SCREEN_HEIGHT]
        self.fog_particles = [p for p in self.fog_particles if 0 <= p[0] < SCREEN_WIDTH * 2]
        
        # Spawn particles only if not fading out
        if not self.is_fading_out:
            if self.weather_type == "rain" and len(self.rain_particles) < self.max_particles["rain"]:
                for _ in range(3):
                    self.rain_particles.append([random.randint(0, SCREEN_WIDTH), 0, random.uniform(200, 300)])
            elif self.weather_type == "snow" and len(self.snow_particles) < self.max_particles["snow"]:
                for _ in range(2):
                    self.snow_particles.append([random.randint(0, SCREEN_WIDTH), 0, random.uniform(50, 100)])
            elif self.weather_type == "fog" and len(self.fog_particles) < self.max_particles["fog"]:
                for _ in range(1):
                    self.fog_particles.append([0, random.randint(0, SCREEN_HEIGHT), random.uniform(20, 50)])

        # Update particle positions
        for particle in self.rain_particles:
            particle[1] += particle[2] * dt
        for particle in self.snow_particles:
            particle[1] += particle[2] * dt
            particle[0] += random.uniform(-10, 10) * dt
        for particle in self.fog_particles:
            particle[0] += particle[2] * dt
                
    def draw(self, surface):
        self.weather_surface.fill((0, 0, 0, 0))
        if self.weather_type == "rain":
            self.weather_surface.fill((0, 0, 0, self.weather_alpha // 2))  # Max 50 alpha
            for x, y, _ in self.rain_particles:
                pygame.draw.line(self.weather_surface, (0, 150, 255, 50), (x, y), (x, y+5), 1)
        elif self.weather_type == "snow":
            self.weather_surface.fill((0, 0, 0, self.weather_alpha // 2))  # Max 50 alpha
            for x, y, _ in self.snow_particles:
                pygame.draw.circle(self.weather_surface, (255, 255, 255, 40), (int(x), int(y)), 2)
        elif self.weather_type == "fog":
            self.weather_surface.fill((0, 0, 0, self.weather_alpha // 2))  # Max 50 alpha
            for x, y, _ in self.fog_particles:
                pygame.draw.rect(self.weather_surface, (150, 150, 150, 30), (x, y, 50, 20))
        surface.blit(self.weather_surface, (0, 0))