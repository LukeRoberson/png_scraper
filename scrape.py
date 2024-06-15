import requests
import re

headers = {
    'Accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(
    'https://api.chess.com/pub/player/networkdirection/games/2022/09',
    headers=headers
)

data = response.json()

for item in data['games']:
    moves = item['pgn']

    # Strip it back to just the moves
    moves = re.sub(r'^\[.*', '', moves, flags=re.MULTILINE)
    moves = moves.strip()
    moves = "\n".join(filter(None, moves.split("\n")))

    # Remove clock times
    moves = re.sub(r'\{.*?\}', '', moves)

    # Cleanup back into a PGN format
    moves = re.sub(r'\d+\.\.\.', '', moves)
    moves = re.sub(r' {2,}', ' ', moves)

    print(moves)

    break
