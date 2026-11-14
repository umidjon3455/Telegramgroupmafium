import random
from collections import Counter

MIN_PLAYERS = 5

class MafiaGame:
    def __init__(self, chat_id: int, host_id: int):
        self.chat_id = chat_id
        self.host_id = host_id
        self.players = {}
        self.phase = "lobby"
        self.votes = {}
        self.night_actions = {}
        self.night = 0

    def add_player(self, user):
        if self.phase != "lobby":
            return False, "O‘yin allaqachon boshlangan."
        if user.id in self.players:
            return False, "Siz allaqachon ro‘yxatdasiz."
        self.players[user.id] = {
            "id": user.id, "name": user.full_name, "username": user.username,
            "alive": True, "role": None,
        }
        return True, "Siz o‘yinga qo‘shildingiz!"

    def remove_player(self, user_id):
        if self.phase != "lobby" or user_id not in self.players:
            return False
        del self.players[user_id]
        return True

    def assign_roles(self):
        ids = list(self.players)
        random.shuffle(ids)
        count = len(ids)
        mafia_count = max(1, count // 4)
        roles = ["mafia"] * mafia_count + ["doctor", "detective"]
        roles += ["citizen"] * (count - len(roles))
        random.shuffle(roles)
        for uid, role in zip(ids, roles):
            self.players[uid]["role"] = role

    def alive_ids(self):
        return [uid for uid, p in self.players.items() if p["alive"]]

    def role_ids(self, role):
        return [uid for uid in self.alive_ids() if self.players[uid]["role"] == role]

    def winner(self):
        mafia = len(self.role_ids("mafia"))
        town = len(self.alive_ids()) - mafia
        if mafia == 0:
            return "town"
        if mafia >= town:
            return "mafia"
        return None

    def eliminate(self, user_id):
        if user_id in self.players:
            self.players[user_id]["alive"] = False

    def day_result(self):
        valid = [v for v in self.votes.values() if v in self.alive_ids()]
        if not valid:
            return None
        counts = Counter(valid)
        highest = max(counts.values())
        leaders = [uid for uid, count in counts.items() if count == highest]
        return leaders[0] if len(leaders) == 1 else None

    def night_result(self):
        mafia_votes = [
            target for actor, target in self.night_actions.items()
            if self.players.get(actor, {}).get("role") == "mafia"
        ]
        if not mafia_votes:
            return None, None
        victim = Counter(mafia_votes).most_common(1)[0][0]
        protected = next(
            (target for actor, target in self.night_actions.items()
             if self.players.get(actor, {}).get("role") == "doctor"),
            None,
        )
        return (None, protected) if victim == protected else (victim, protected)
