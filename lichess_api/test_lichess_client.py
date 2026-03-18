import unittest
import os
from datetime import datetime, timedelta

from lichess_api.lichess_client import GamesUser, UserRatingHistory


class TestLichessClient(unittest.TestCase):
    def test_games_user(self):
        # given
        username = "Emanuel_Kassler"
        token = os.environ.get("LICHESS_API_KEY_EMANUEL_KASSLER")
        games_user = GamesUser(username, token)
        since = datetime.now() - timedelta(weeks=1)

        # when
        games = games_user.execute(since=since)

        # then
        game = next(games)
        self.assertIsNotNone(game)
        self.assertIn(username, [game_player.user.name for game_player in game.players.values()])

    def test_user_rating_history(self):
        # given
        username = "Emanuel_Kassler"
        token = os.environ.get("LICHESS_API_KEY_EMANUEL_KASSLER")
        user_rating_history = UserRatingHistory(username, token)
        some_unachievable_elo = 4000

        # when
        rating = user_rating_history.execute()

        # then
        self.assertIsNotNone(rating)
        self.assertTrue(0 < rating.ratings['Blitz'][0].value < some_unachievable_elo)


if __name__ == "__main__":
    unittest.main()
