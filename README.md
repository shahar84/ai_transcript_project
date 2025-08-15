# AI Transcript Project

## What it does
This script:
1. Extracts audio from a video file (e.g. an interview with Steve Jobs)
2. Sends the audio to Replicate's incredibly-fast-whisper model for transcription
3. Prints the resulting transcription JSON

## Setup
1. Install dependencies:
```
pip install -r requirements.txt
```

2. Add your Replicate API token and whisper model version to `main.py`.

## Run
Place `steve-interview.mp4` in the same directory and run:
```
python main.py
```
