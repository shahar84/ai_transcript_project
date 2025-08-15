# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Python project that extracts audio from video files and transcribes them using Replicate's Whisper model. The main workflow is: video → audio extraction → AI transcription.

## Setup and Dependencies
Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application
```bash
python main.py
```

Note: Before running, you need to:
1. Add your Replicate API token to the `REPLICATE_API_TOKEN` variable in `main.py`
2. Place a video file named `steve-interview.mp4` in the project root

## Architecture
- `main.py` - Single-file application with three main functions:
  - `extract_audio()` - Uses MoviePy to extract audio from video files
  - `transcribe_audio()` - Sends audio to Replicate's Whisper API for transcription
  - `main()` - Orchestrates the workflow and outputs JSON results

## API Integration
Uses Replicate's incredibly-fast-whisper model for transcription. The application makes HTTP requests to `https://api.replicate.com/v1/predictions` with the audio file and language parameters.