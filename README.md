# Chess PNG Game Scraper
Downloads chess games in PGN format from chess.com, and stores in JSON files

The JSON file contains the original PGN, as well the result of the game, and each pair of moves as a separate entry for easy parsing.

This only scrapes publically available information from chess.com


## How it works
The simplest way to use this is to the get_all_games() function, passing:
* A player name
* A starting year
* An ending year

This will get all games for this player, and store the details in a JSON file based on the year. If the player didn't play any games in that year, no file will be created.

If a JSON file has already been downloaded for the player/year, it will be skipped. This prevents scraping the same thing again and again needlessly.

If there was no games for a player/year, this is added to skip.txt. This way we can skip scraping this again, knowing it will be empty.


## JSON Format
The main format is:
```
{
    year: {
        month: [
            game-1,
            game-2,
            game-n
        ]
    }
}
```

Within each game, the format is:
```
{
    pgn: Raw PGN game,
    result: Game result,
    1: [white, black],
    2: [white, black],
    n: [white, black],
}
```
