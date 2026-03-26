# WAV Generator

Browser-based tool for generating randomized WAV audio files. Combines a rhythm pattern (kick/snare at 130 BPM) with a random melody using C major scale notes.

Built with Python and Flask. Terminal-style UI.

## Features

- Set base filename, number of tracks, duration, and increment per file
- Files download directly to your machine
- Each generated track is unique

## Stack

- Python / Flask
- pydub + numpy for audio generation
- Deployed on Render

## Run locally

```bash
pip install -r requirements.txt
python app.py
```
