# camera.py
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, MAP_WIDTH, MAP_HEIGHT

class Camera:
    def __init__(self, target):
        self.target = target
        self.x = 0
        self.y = 0
        self.smoothness = 0.1

    def update(self):
        target_x = self.target.rect.centerx - SCREEN_WIDTH // 2
        target_y = self.target.rect.centery - SCREEN_HEIGHT // 2
        self.x += (target_x - self.x) * self.smoothness
        self.y += (target_y - self.y) * self.smoothness
        self.x = max(0, min(self.x, MAP_WIDTH - SCREEN_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT - SCREEN_HEIGHT))
