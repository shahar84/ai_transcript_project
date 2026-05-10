# Step 7: Generating Your Podcast Audio

## What We're Building

You have a polished podcast script. Now we turn it into actual audio — spoken in a natural AI voice — using Gemini TTS via Replicate.

```
podcast/script.txt  -->  Replicate Gemini TTS  -->  podcast/episode.wav
```

Same Replicate account you already have. No new setup required.

---

## How It Works

We use [Gemini TTS](https://replicate.com/google/gemini-3.1-flash-tts) — a text-to-speech model that supports named voices and style instructions. You choose a voice by name and describe how it should sound in plain English. No voice sample or recording needed.

---

## Step 1: Generate the Podcast Audio

```bash
uv run transcript podcast my-project
```

This will:
1. Read `projects/my-project/podcast/script.txt`
2. Split it into sentence-sized chunks (the model has a character limit per request)
3. Send each chunk to Replicate with your chosen voice and style
4. Stitch all the audio pieces together
5. Save the final episode as `projects/my-project/podcast/episode.wav`

You will see progress printed for each chunk:

```
Synthesizing chunk 1/8...
Synthesizing chunk 2/8...
...
Podcast episode saved to: projects/my-project/podcast/episode.wav
```

---

## Choosing a Voice

The default voice is **Kore**. To use a different one:

```bash
uv run transcript podcast my-project --voice-name Zephyr
```

Available voices:

```
Achernar  Achird     Algenib    Algieba    Alnilam    Aoede
Autonoe   Callirrhoe Charon     Despina    Enceladus  Erinome
Fenrir    Gacrux     Iapetus    Kore       Laomedeia  Leda
Orus      Pulcherrima Puck      Rasalgethi Sadachbia  Sadaltager
Schedar   Sulafat    Umbriel    Vindemiatrix Zephyr   Zubenelgenubi
```

Try a few and see which sounds best for your content.

---

## Changing the Speaking Style

The `TTS_PROMPT` setting in `config.py` controls how the voice speaks. The default is:

```
Speak in an engaging, conversational podcast tone.
```

You can change it to anything:

```
Speak slowly and clearly, like a documentary narrator.
Speak with energy and excitement, like a sports commentator.
Speak calmly and warmly, like a therapist.
```

To override it without editing the code, add `TTS_PROMPT` to your `.env` file:

```
TTS_PROMPT=Speak slowly and clearly, like a documentary narrator.
```

---

## Under the Hood: `tts.py`

Open `tts.py`. There are two main pieces:

### `_split_into_chunks(text)`

Gemini TTS has a character limit per request. This function splits the script into sentence-sized pieces so each one fits within that limit.

### `synthesize_podcast(script_text, output_path, voice_name, prompt, language_code)`

The main function. It:
1. Splits the script into chunks
2. Sends each chunk to Replicate with the chosen voice and style prompt
3. Downloads the audio for each chunk as a NumPy array
4. Concatenates all arrays into one
5. Writes the final WAV file

---

## Listening to the Result

Open `projects/my-project/podcast/episode.wav` in any audio player.

If something sounds off:
- **Abbreviations and symbols** get read literally — write "for example" not "e.g.", "percent" not "%"
- **Try a different voice** — some voices suit certain content better
- **Adjust the style prompt** — the tone instruction has a big effect on pacing and feel

---

## You Built the Full Pipeline

Here is everything this project does, end to end:

```
YouTube URL
    --> download video           (yt-dlp)
    --> extract audio            (MoviePy)
    --> transcribe speech        (Whisper via Replicate)
    --> rewrite as podcast       (OpenAI GPT-4o-mini)
    --> synthesize audio         (Gemini TTS via Replicate)
    --> podcast/episode.wav
```

Drop YouTube URLs in `urls.txt`, run three commands, get a podcast episode.

---

## Checkpoint

- [ ] `uv run transcript podcast my-project` ran without errors
- [ ] `projects/my-project/podcast/episode.wav` exists
- [ ] I listened to the output and the voice sounds natural

---

Next: [What You Can Build Next](./step-08-whats-next.md)
