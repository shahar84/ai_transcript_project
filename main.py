"""Audio Transcription Tool

This module provides functionality to extract audio from video files and transcribe
them using Replicate's Whisper model. The workflow is:
1. Extract audio from video file → save as .mp3 in output folder
2. Transcribe audio using AI → save as .txt and .json in output folder

All output files maintain the same base name as the input video file.
Example: "steve-interview.mp4" → "steve-interview.mp3", "steve-interview.txt", "steve-interview.json"
"""

from moviepy.editor import VideoFileClip
import json
import replicate
import os
from pathlib import Path

from config import settings

# Set up replicate client with API token
replicate.Client(api_token=settings.REPLICATE_API_TOKEN)


def extract_audio(video_path, output_folder="output"):
    """Extract audio from a video file and save as MP3.
    
    Args:
        video_path (str): Path to the input video file
        output_folder (str): Directory to save the extracted audio (default: "output")
        
    Returns:
        str: Path to the extracted audio file
        
    Example:
        >>> extract_audio("videos/interview.mp4")
        "output/interview.mp3"
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get video filename without extension
    video_filename = Path(video_path).stem

    # Create audio output path
    audio_output_path = os.path.join(output_folder, f"{video_filename}.mp3")

    clip = VideoFileClip(video_path)
    clip.audio.write_audiofile(audio_output_path)
    return audio_output_path


def transcribe_audio(file_path):
    """Transcribe audio file using Replicate's Whisper model.
    
    Args:
        file_path (str): Path to the audio file to transcribe
        
    Returns:
        dict: Transcription result containing:
            - 'text': Full transcribed text
            - 'chunks': List of text segments with timestamps
            
    Example:
        >>> transcribe_audio("output/interview.mp3")
        {
            "text": "Hello world...",
            "chunks": [{"text": "Hello", "timestamp": [0, 1.5]}, ...]
        }
    """
    # Use incredibly-fast-whisper model via Replicate API
    output = replicate.run(
        settings.TRANSCRIBE_MODEL,
        input={
            "audio": open(file_path, "rb")
        }
    )

    return output


def save_transcription(transcription_data, video_path, output_folder="output"):
    """Save transcription data to text and JSON files.
    
    Args:
        transcription_data (dict): Transcription result from transcribe_audio()
        video_path (str): Original video file path (used for naming output files)
        output_folder (str): Directory to save files (default: "output")
        
    Returns:
        tuple: (text_file_path, json_file_path)
        
    Example:
        >>> save_transcription(result, "videos/interview.mp4")
        ("output/interview.txt", "output/interview.json")
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get video filename without extension
    video_filename = Path(video_path).stem

    # Save as text file (plain text transcription)
    text_output_path = os.path.join(output_folder, f"{video_filename}.txt")
    with open(text_output_path, 'w', encoding='utf-8') as f:
        f.write(transcription_data['text'])

    # Save as JSON file (full data with timestamps)
    json_output_path = os.path.join(output_folder, f"{video_filename}.json")
    with open(json_output_path, 'w', encoding='utf-8') as f:
        json.dump(transcription_data, f, indent=2, ensure_ascii=False)

    return text_output_path, json_output_path


def main():
    """Main function to orchestrate the video transcription workflow.
    
    Process:
    1. Extract audio from video file
    2. Transcribe audio using AI
    3. Save results in multiple formats
    
    Returns:
        dict: Transcription result data
    """
    video_path = "videos/steve-interview.mp4"

    print(f"Starting transcription workflow for: {video_path}")
    print("-" * 50)

    # Step 1: Extract audio to output folder with proper naming
    print("1. Extracting audio from video...")
    audio_path = extract_audio(video_path)

    # Step 2: Transcribe the audio using Replicate AI
    print("2. Transcribing audio (this may take a moment)...")
    result = transcribe_audio(audio_path)

    # Step 3: Save transcription to files
    print("3. Saving transcription files...")
    text_path, json_path = save_transcription(result, video_path)

    print("-" * 50)
    print("✅ Transcription completed successfully!")
    print(f"📁 Audio saved to: {audio_path}")
    print(f"📄 Transcription saved to: {text_path}")
    print(f"📊 Full data saved to: {json_path}")

    return result


if __name__ == "__main__":
    """Entry point when script is run directly."""
    main()
