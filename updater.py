import argparse
from datetime import timedelta

from lichess_api.lichess_client import UserRatingHistory, GamesUser
from persistence.db_client import DbClient

def main(username, api_token=None, database_path=None):
    database_path = database_path or f"{username}.chessgames.db"
    db_client = DbClient(database_path, "schema.sql")
    db_client.init_db()

    game = db_client.get_most_recent_game()
    since = game.created_at + timedelta(milliseconds=1) if game else None
    count = 0
    for game in GamesUser(username, api_token).execute(since):
        db_client.insert(game)
        count += 1
        if count % 100 == 0:
            print(f"Inserted {count} games...")
    print(f"Added {count} games...")

    user_rating_history = UserRatingHistory(username, api_token).execute()
    db_client.insert_rating_history(user_rating_history)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import chess games from Lichess.")
    parser.add_argument("username", type=str, help="Lichess username")
    parser.add_argument("--api_token", type=str, default=None, help="Lichess API token (optional, speeds up download if provided)")
    args = parser.parse_args()
    main(args.username, args.api_token)
