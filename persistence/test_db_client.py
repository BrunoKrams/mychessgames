import unittest
import tempfile
import os
from datetime import datetime
from model import Game, Player, Color
from persistence.db_client import DbClient

class TestSQLiteClient(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, 'test_chess.db')
        self.schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        self.client = DbClient(db_path=self.db_path, schema_path=self.schema_path)
        self.client.init_db()

    def tearDown(self):
        self.client.cursor.close()
        self.client.conn.close()
        self.temp_dir.cleanup()

    def test_insert_game(self):
        # given
        player_white = Player(rating=1500, id='p1', name='Alice')
        player_black = Player(rating=1400, id='p2', name='Bob')
        players = {Color.WHITE: player_white, Color.BLACK: player_black}
        game = Game(
            id='g1',
            variant='standard',
            speed='blitz',
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            last_move_at=datetime(2023, 1, 1, 12, 10, 0),
            players=players,
            winner=Color.WHITE,
            moves='e4 e5 Nf3 Nc6'
        )

        # when
        self.client.insert(game)

        # then
        self.client.cursor.execute('SELECT * FROM games WHERE id=?', (game.id,))
        game_row = self.client.cursor.fetchone()
        self.assertIsNotNone(game_row)
        self.assertEqual(game_row[0], 'g1')
        self.assertEqual(game_row[1], 'standard')

        self.client.cursor.execute('SELECT * FROM players WHERE id=?', (player_white.id,))
        self.assertIsNotNone(self.client.cursor.fetchone())
        self.client.cursor.execute('SELECT * FROM players WHERE id=?', (player_black.id,))
        self.assertIsNotNone(self.client.cursor.fetchone())

        self.client.cursor.execute('SELECT * FROM game_players WHERE game_id=? AND color=?', (game.id, 'white'))
        assoc_white = self.client.cursor.fetchone()
        self.assertIsNotNone(assoc_white)

if __name__ == '__main__':
    unittest.main()

