# AI Transcript Project

A Python application that extracts audio from video files and transcribes them using Replicate's Whisper model. The main workflow is: video → audio extraction → AI transcription.

## Prerequisites
- Python 3.x
- Replicate API account and token

## Setup
1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add your Replicate API token to the `REPLICATE_API_TOKEN` variable in `main.py`

4. Place a video file in the project `videos` folder

## Usage
```bash
python main.py
```

## Architecture
The application consists of three main functions in `main.py`:

- `extract_audio()` - Uses MoviePy to extract audio from video files
- `transcribe_audio()` - Sends audio to Replicate's Whisper API for transcription  
- `main()` - Orchestrates the workflow and outputs JSON results

## API Integration
Uses Replicate's incredibly-fast-whisper model for transcription. The application makes HTTP requests to `https://api.replicate.com/v1/predictions` with the audio file and language parameters.

## Output
The application outputs transcription results in JSON format.
