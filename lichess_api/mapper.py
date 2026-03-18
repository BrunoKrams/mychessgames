from utils.datatime_converter import DateTimeConverter
from model import Game, GamePlayer, User, Color, Opening, RatingPoint, RatingHistory


class GameMapper:

    def __init__(self):
        self.converter = DateTimeConverter()

    def map(self, data: dict) -> Game:
        players = {}
        for color_str in ["white", "black"]:
            player_data = data["players"][color_str]
            user_data = player_data.get("user", {})
            user = User(
                id=user_data.get("id", ""),
                name=user_data.get("name", ""),
                title=user_data.get("title", "")
            )
            game_player = GamePlayer(
                rating=player_data.get("rating", -1),
                user=user
            )
            players[Color.WHITE if color_str == "white" else Color.BLACK] = game_player
        winner_str = data.get("winner")
        if winner_str == "white":
            winner = Color.WHITE
        elif winner_str == "black":
            winner = Color.BLACK
        else:
            winner = None
        created_at = self.converter.to_datetime(data["createdAt"])
        last_move_at = self.converter.to_datetime(data["lastMoveAt"])
        opening_data = data.get("opening")
        opening = None if opening_data is None else Opening(
            eco=opening_data["eco"],
            name=opening_data.get("name", ""),
            ply=opening_data.get("ply", -1),
        )
        return Game(
            id=data["id"],
            variant=data["variant"],
            speed=data["speed"],
            created_at=created_at,
            last_move_at=last_move_at,
            players=players,
            opening=opening,
            winner=winner,
            moves=data["moves"]
        )


class RatingMapper:

    def __init__(self, username: str):
        self.username = username

    def map(self, data: list):
        from datetime import datetime
        ratings_dict = {}
        for rating_dict in data:
            name = rating_dict.get("name", "")
            points = []
            for point in rating_dict.get("points", []):
                year, month, day, value = point
                date = datetime(year, month + 1, day)  # month from lichess is zero-based
                points.append(RatingPoint(date, value))
            ratings_dict[name] = points
        return RatingHistory(username=self.username, ratings=ratings_dict)
