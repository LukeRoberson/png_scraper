import requests
import re
import json
from tqdm import tqdm
import datetime


BASE_URL = 'https://api.chess.com/pub/player/'
MONTHS = [f'{i:02}' for i in range(1, 13)]


def get_games_restapi(player, year, month):
    # API call to get games for the month/year
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Chrome/58.0.3029.110'
    }

    response = requests.get(
        f'{BASE_URL}{player}/games/{year}/{month}',
        headers=headers
    )

    data = response.json()
    return data['games']


def game_to_dict(pgn):
    # Strip it back to just the moves
    moves = re.sub(r'^\[.*', '', pgn, flags=re.MULTILINE)
    moves = moves.strip()
    moves = "\n".join(filter(None, moves.split("\n")))

    # Remove clock times
    moves = re.sub(r'\{.*?\}', '', moves)

    # Cleanup back into a PGN format
    moves = re.sub(r'\d+\.\.\.', '', moves)
    moves = re.sub(r' {2,}', ' ', moves)

    # Split the moves into a list, and extract the result
    result = moves.split(' ')[-1]
    moves = moves.rstrip(result)
    split_moves = [
        move.strip() for move in re.split(r'(?<= )(?=\d+\.)', moves)
    ]

    # Create a dictionary to store the game
    game_dict = {
        'pgn': moves,
        'result': result
    }

    # Loop through the moves and add them to the dictionary
    try:
        for move in split_moves:
            move_number = re.match(r'\d+', move).group()
            each_move = move.split(' ')
            del each_move[0]
            game_dict[move_number] = each_move

    # Skip any invalid game
    except AttributeError:
        pass

    return game_dict


def get_all_games(player, start_year, end_year):
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime('%m')

    for year in range(start_year, end_year + 1):
        # Create a dictionary to store the games
        month_dict = {
            year: {}
        }

        for month in tqdm(MONTHS):
            # Skip any future months
            if (year > current_year) or (year == current_year and month > current_month):
                continue

            # API call to get games for the month/year
            games = get_games_restapi(
                player=player,
                year=year,
                month=month
            )
            if len(games) == 0:
                continue

            # Loop through the games and convert them to a dictionary
            month_dict[year][month] = []
            for item in games:
                moves = item['pgn']
                game_dict = game_to_dict(moves)

                month_dict[year][month].append(game_dict)

        if not month_dict[year]:
            continue

        # Save game_dict to a JSON file
        file_path = f'./dumps/{player}-{year}.json'
        with open(file_path, 'w') as file:
            json.dump(month_dict, file)


if __name__ == '__main__':
    player = 'networkdirection'

    get_all_games(player, 2021, 2025)
