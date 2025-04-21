# time_system.py
from settings import REAL_SECONDS_PER_GAME_DAY

class TimeSystem:
    def __init__(self):
        self.year = 1
        self.month = 1
        self.day = 1
        self.hour = 6
        self.minute = 0
        self.seconds_accumulated = 0.0
        self.real_seconds_per_game_day = REAL_SECONDS_PER_GAME_DAY
        self.game_seconds_per_real_second = (24 * 3600) / self.real_seconds_per_game_day

    def set_time_scale(self, real_seconds_per_game_day):
        self.real_seconds_per_game_day = real_seconds_per_game_day
        self.game_seconds_per_real_second = (24 * 3600) / self.real_seconds_per_game_day
        
    def update(self, dt):
        self.seconds_accumulated += dt
        game_seconds = self.seconds_accumulated * self.game_seconds_per_real_second
        new_minutes = int(game_seconds // 60)
        self.seconds_accumulated -= (new_minutes * 60) / self.game_seconds_per_real_second
        self.minute += new_minutes
        # Roll over minutes
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        # Roll over hours
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
        # Roll over days
        while self.day > 30:  # 30 days per month
            self.day -= 30
            self.month += 1
        # Roll over months
        while self.month > 12:  # 12 months per year
            self.month -= 12
            self.year += 1

    def get_time_string(self):
        return f"{self.day}/{self.month}/{self.year} - {self.hour:02d}:{self.minute:02d}"

    def get_lighting_alpha(self):
        hour = self.hour + self.minute / 60.0
        if 6 <= self.hour < 12:
            return 0  # Morning: Full brightness
        elif 12 <= hour < 13:
            return 50 * (hour - 12) # Noon: Brightest
        elif 12 <= hour < 18:
            return 50  # Afternoon: Slight dim
        elif 18 <= hour < 19:
            return 50 + 50 * (hour - 18) # Evening: Dimming
        elif 19 <= hour < 21:
            return 100 # Evening: Dimming more
        elif 21 <= hour < 22:
            return 100 + 50 * (hour - 21)  # Evening: Darker
        elif 22 <= hour < 24:
            return 150 * (hour - 22) # Night: Darkening
        elif 0 <= hour < 3:
            return 150 + 50 * (hour - 0) # Night: Darkening more
        elif 3 <= hour < 6:
            return 150 + 50 * (hour - 3) # Night: Darkening more    
        else:
            return 0  # Invalid hour, return full brightness