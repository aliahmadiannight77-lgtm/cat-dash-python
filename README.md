# Cat Dash

A polished, self-contained endless runner made with Python and Pygame. Guide a
little cat through a moonlit garden, jump over plants and parcels, and see how
far you can go. The art is drawn in code, so there are no external images,
fonts, or audio files to download.

## Requirements

- Python 3.10 or newer
- Pygame CE 2.5 or newer (the drop-in Pygame-compatible edition)

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

## Controls

- **Space**, **Up**, **W**, or **left-click**: start, then jump
- **Esc**: quit

The game gets faster as the distance grows. Your best distance is saved locally
in `cat_dash_record.json` in the folder where you run the game.

## Project

Cat Dash is an original, asset-free Python game inspired by the pick-up-and-play
feel of classic endless runners. It includes a parallax night sky, an animated
cat, randomized obstacles, collision/game-over handling, and a local high score.

## License

Released under the MIT License. See [LICENSE](LICENSE).
