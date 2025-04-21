# quest.py
class Quest:
    def __init__(self, name, description, target_npc, deadline_hour, reward, npc=None):
        self.name = name
        self.description = description
        self.target_npc = target_npc
        self.deadline_hour = deadline_hour
        self.reward = reward
        self.npc = npc
        self.active = False
        self.completed = False
        
    def notify(self, status):
        return {
            "name": self.name,
            "description": self.description,
            "status": status
        }

    def check_completion(self, player, npc, time_system):
        if self.active and not self.completed:
            if time_system.hour >= self.deadline_hour:
                self.active = False
                if self.npc:
                    self.npc.quest_status = "failed"
                    self.npc.reset_quest_state()
                print(f"Quest '{self.name}' failed: Time expired.")
                return self.notify("Quest Failed!")
            elif npc == self.target_npc and player.interaction_prompt["text"] == npc.interact(player)["text"]:
                self.completed = True
                self.active = False
                player.inventory.add_item(self.reward)
                if self.npc:
                    self.npc.quest_status = "completed"
                    self.npc.reset_quest_state()
                print(f"Quest '{self.name}' completed! Reward: {self.reward}")
                return self.notify("Quest Completed!")
        return None

    def start(self):
        self.active = True
        print(f"Quest '{self.name}' started: {self.description}")
        return self.notify("Quest Started!")

    def get_progress(self):
        if self.completed:
            return "Completed"
        elif not self.active:
            return "Failed"
        return f"Deliver to {self.target_npc.name}: {'Yes' if self.completed else 'No'}"

    def get_time_info(self):
        return f"Deadline: {self.deadline_hour:02d}:00"

class KillQuest:
    def __init__(self, name, description, target_enemy, start_hour, end_hour, reward, npc=None):
        self.name = name
        self.description = description
        self.target_enemy = target_enemy
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.reward = reward
        self.npc = npc
        self.active = False
        self.completed = False
    
    def notify(self, status):
        return {
            "name": self.name,
            "description": self.description,
            "status": status
        }

    def check_completion(self, player, enemy, time_system):
        if self.active and not self.completed:
            if not (self.start_hour <= time_system.hour < self.end_hour or 
                    (self.end_hour < self.start_hour and (time_system.hour >= self.start_hour or time_system.hour < self.end_hour))):
                self.active = False
                if self.npc:
                    self.npc.quest_status = "failed"
                    self.npc.reset_quest_state()
                print(f"Quest '{self.name}' failed: Time window expired.")
                return self.notify("Quest Failed!")
            elif enemy == self.target_enemy and not enemy.alive:
                self.completed = True
                self.active = False
                player.inventory.add_item(self.reward)
                if self.npc:
                    self.npc.quest_status = "completed"
                    self.npc.reset_quest_state()
                print(f"Quest '{self.name}' completed! Reward: {self.reward}")
                return self.notify("Quest Completed!")
        return None

    def start(self):
        self.active = True
        print(f"Quest '{self.name}' started: {self.description}")
        return self.notify("Quest Started!")

    def get_progress(self):
        if self.completed:
            return "Completed"
        elif not self.active:
            return "Failed"
        return f"Kill {self.target_enemy.name}: {'Yes' if not self.target_enemy.alive else 'No'}"

    def get_time_info(self):
        return f"Time: {self.start_hour:02d}:00-{self.end_hour:02d}:00"