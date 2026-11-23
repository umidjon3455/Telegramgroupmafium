import unittest

from bot.game import MafiaGame


class NightVoteTests(unittest.TestCase):
    def setUp(self):
        self.game = MafiaGame(chat_id=-100, host_id=1)
        self.game.players = {
            1: {"id": 1, "name": "Mafia 1", "alive": True, "role": "mafia"},
            2: {"id": 2, "name": "Mafia 2", "alive": True, "role": "mafia"},
            3: {"id": 3, "name": "Doctor", "alive": True, "role": "doctor"},
            4: {"id": 4, "name": "Citizen A", "alive": True, "role": "citizen"},
            5: {"id": 5, "name": "Citizen B", "alive": True, "role": "citizen"},
        }

    def test_tied_mafia_votes_do_not_eliminate_anyone(self):
        self.game.night_actions = {1: 4, 2: 5, 3: 4}

        self.assertEqual(self.game.night_result(), (None, 4))

    def test_majority_mafia_vote_selects_victim(self):
        self.game.night_actions = {1: 4, 2: 4, 3: 5}

        self.assertEqual(self.game.night_result(), (4, 5))

    def test_doctor_saves_selected_victim(self):
        self.game.night_actions = {1: 4, 2: 4, 3: 4}

        self.assertEqual(self.game.night_result(), (None, 4))

    def test_no_mafia_vote_has_no_victim(self):
        self.game.night_actions = {3: 4}

        self.assertEqual(self.game.night_result(), (None, None))


if __name__ == "__main__":
    unittest.main()
