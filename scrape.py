import requests
import re
import json
from tqdm import tqdm
import datetime
import os
import time
from concurrent.futures import ThreadPoolExecutor


BASE_URL = 'https://api.chess.com/pub/player/'
MONTHS = [f'{i:02}' for i in range(1, 13)]
TITLES = ['GM', 'WGM', 'IM', 'WIM', 'FM', 'WFM', 'NM', 'WNM', 'CM', 'WCM']


def get_players_restapi(title):
    # API call to get a list of players by their title
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Chrome/58.0.3029.110'
    }

    response = requests.get(
        f'https://api.chess.com/pub/titled/{title}',
        headers=headers
    )

    data = response.json()
    return data['players']


def get_games_restapi(player, year, month):
    # API call to get games for the month/year
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'Chrome/58.0.3029.110'
    }

    try:
        response = requests.get(
            f'{BASE_URL}{player}/games/{year}/{month}',
            headers=headers
        )

        data = response.json()
        return data['games']

    except Exception as e:
        print(f'Error {e} getting games for {player}-{year}-{month}')
        time.sleep(5)
        return []


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

    # Remove any '@' symbols which sometimes appear in the moves
    #   It's unclear what they mean, but they're not needed
    moves = moves.replace('@', '')

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


def get_all_games(player, start_year=2010, end_year=2024):
    # This gets all the games for a player between given years
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime('%m')

    for year in range(start_year, end_year + 1):
        # Create a dictionary to store the games
        month_dict = {
            year: {}
        }

        # Check if a file already exists for the player and year
        file_path = f'./dumps/{player}-{year}.json'
        if os.path.exists(file_path):
            continue

        # Check if we've previously skipped this player/year
        skip_file = 'skip.txt'
        if os.path.exists(skip_file):
            with open(skip_file, 'r') as file:
                skipped = file.read().splitlines()
            if f'{player}-{year}.json' in skipped:
                continue

        pbar = tqdm(MONTHS, colour='green', leave=False)
        for month in pbar:
            pbar.set_description(f'Player: {player}, {year}')
            # Skip any future months
            if (
                (year > current_year) or
                (year == current_year and month > current_month)
            ):
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
            try:
                for item in games:
                    moves = item['pgn']
                    game_dict = game_to_dict(moves)

                    month_dict[year][month].append(game_dict)
            except KeyError:
                with open('skip.txt', 'a') as file:
                    file.write(f'{player}-{year}.json\n')

        if not month_dict[year]:
            with open('skip.txt', 'a') as file:
                file.write(f'{player}-{year}.json\n')
            continue

        # Save game_dict to a JSON file
        file_path = f'./dumps/{player}-{year}.json'
        with open(file_path, 'w') as file:
            json.dump(month_dict, file)


if __name__ == '__main__':
    player_list = []

    # Get all titled players (more than 12k players)
    for title in tqdm(TITLES, desc='Getting Titled Players', colour='blue'):
        data = get_players_restapi(title)
        player_list.extend(data)

    print(f'{len(player_list)} titled players found')
    player_list.sort()

    with ThreadPoolExecutor(max_workers=12) as executor:
        results = list(
            tqdm(
                executor.map(
                    get_all_games,
                    player_list
                ),
                total=len(player_list),
                colour='yellow',
                desc='Total Progress',
            )
        )
