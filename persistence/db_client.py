import os
import sqlite3

from utils.datatime_converter import DateTimeConverter
from model import Color, Game, RatingHistory, RatingPoint


class DbClient:
    __PROBE_QUERY = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"

    def __init__(self, db_path: str = "chess.db", schema_path: str = None):
        self.schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.converter = DateTimeConverter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = None
        self.conn = None

    def init_db(self):
        if self.__database_exists():
            print("Database already exists.")
            return
        with open(self.schema_path, "r") as f:
            schema = f.read()
            self.cursor.executescript(schema)
            self.conn.commit()
            print(f"Database initialized at: {self.db_path}")

    def __database_exists(self):
        if os.path.exists(self.db_path):
            self.cursor.execute(self.__PROBE_QUERY)
            return self.cursor.fetchone()
        return False

    def get_most_recent_game(self) -> Game:
        """
        Retrieves the most recent game from the database based on the latest 'created_at' timestamp.
        Returns:
            Game: The most recent Game object, or None if no games exist.
        """
        self.cursor.execute(
            """
            SELECT g.id,
                   g.variant,
                   g.speed,
                   g.created_at,
                   g.last_move_at,
                   g.winner,
                   g.moves,
                   o.eco,
                   o.name,
                   o.ply
            FROM games g
                     LEFT JOIN openings o ON g.opening_eco = o.eco
            ORDER BY g.created_at DESC LIMIT 1
            """
        )
        row = self.cursor.fetchone()
        if row is None:
            return None
        from model import Game, Opening, GamePlayer, User, Color
        opening = None
        if row[7] is not None:
            opening = Opening(eco=row[7], name=row[8], ply=row[9])

        self.cursor.execute(
            """
            SELECT gp.color, p.id, p.name, p.title, gp.rating
            FROM game_players gp
                     JOIN players p ON gp.player_id = p.id
            WHERE gp.game_id = ?
            """,
            (row[0],)
        )
        players = {}
        for color_str, player_id, player_name, player_title, rating in self.cursor.fetchall():
            color = Color.WHITE if color_str.lower() == 'white' else Color.BLACK
            user = User(id=player_id, name=player_name, title=player_title)
            game_player = GamePlayer(rating=rating, user=user)
            players[color] = game_player
        return Game(
            id=row[0],
            variant=row[1],
            speed=row[2],
            created_at=self.converter.to_datetime(row[3]),
            last_move_at=self.converter.to_datetime(row[4]),
            players=players,
            opening=opening,
            winner=row[5],
            moves=row[6]
        )

    def insert(self, game: Game):
        if game.opening is not None:
            self.cursor.execute(
                """
                INSERT
                OR IGNORE INTO openings (eco, name, ply) VALUES (?, ?, ?)
                """,
                (game.opening.eco, game.opening.name, game.opening.ply)
            )

        self.cursor.execute(
            """
            INSERT INTO games (id, variant, speed, created_at, last_move_at, winner, moves, opening_eco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                game.id,
                game.variant,
                game.speed,
                self.converter.to_unix_epoch(game.created_at),
                self.converter.to_unix_epoch(game.last_move_at),
                None if game.winner is None else ('white' if game.winner == Color.WHITE else 'black'),
                game.moves,
                game.opening.eco if game.opening is not None else None
            )
        )

        for color, game_player in game.players.items():
            user = game_player.user
            self.cursor.execute(
                """
                INSERT
                OR IGNORE INTO players (id, name, title) VALUES (?, ?, ?)
                """,
                (user.id, user.name, user.title)
            )
            self.cursor.execute(
                """
                INSERT INTO game_players (game_id, color, player_id, rating)
                VALUES (?, ?, ?, ?)
                """,
                (
                    game.id,
                    'white' if color.name.lower() == 'white' else 'black',
                    user.id,
                    game_player.rating
                )
            )
        self.conn.commit()

    def get_rating_history(self) -> dict:
        """
        Returns all rating time series from the database.
        Returns:
            dict: { rating_name: [(date_str, value), ...] } sorted by date ascending.
        """
        self.cursor.execute(
            """
            SELECT r.name, rp.date, rp.value
            FROM rating_points rp
            JOIN ratings r ON rp.rating_id = r.id
            ORDER BY r.name, rp.date ASC
            """
        )
        rows = self.cursor.fetchall()
        result = {}
        for name, date, value in rows:
            result.setdefault(name, []).append((date, value))
        return result

    def insert_rating_history(self, rating_history):
        """
        Insert all ratings and their points for a player from a RatingHistory object.
        Args:
            rating_history (RatingHistory): The rating history object.
        """
        player_id = rating_history.username
        for rating_name, points in rating_history.ratings.items():
            # Insert or ignore the rating
            self.cursor.execute(
                """
                INSERT OR IGNORE INTO ratings (player_id, name) VALUES (?, ?)
                """,
                (player_id, rating_name)
            )
            self.cursor.execute(
                """
                SELECT id FROM ratings WHERE player_id = ? AND name = ?
                """,
                (player_id, rating_name)
            )
            rating_id = self.cursor.fetchone()[0]
            for point in points:
                date_str = point.date.isoformat()  # Store as ISO string
                value = point.value
                self.cursor.execute(
                    """
                    INSERT OR IGNORE INTO rating_points (rating_id, date, value)
                    VALUES (?, ?, ?)
                    """,
                    (rating_id, date_str, value)
                )
        self.conn.commit()
