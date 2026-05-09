# Step 8: Generating Your Podcast in Your Own Voice

## What We're Building

You have a polished podcast script. Now we turn it into actual audio — spoken in your own voice — using AI voice cloning via Replicate.

```
podcast script .txt  +  your voice sample .wav  -->  Replicate XTTS v2  -->  podcast episode .wav
```

Same Replicate account you already have. No new setup required.

---

## How Voice Cloning Works

We use [XTTS v2](https://replicate.com/lucataco/xtts-v2) by Coqui — a state-of-the-art voice cloning model. You give it a short recording of your voice and it learns to speak in that style. It extracts your pitch, rhythm, and tone and applies them to any text.

You need:
- A WAV recording of yourself (30–60 seconds is ideal)
- Clear audio with no background noise or music
- You can read anything — a few paragraphs from a book, a news article, whatever feels natural

---

## Step 1: Record Your Voice

Record yourself speaking normally for 30–60 seconds. Use your phone, laptop microphone, or any recording app.

Export it as a **WAV file** and save it somewhere easy to find:

```bash
mkdir voices
# save your recording as voices/my-voice.wav
```

Tips for a good recording:
- Quiet room, no echo
- Normal speaking pace — do not slow down or exaggerate
- Hold the microphone at a consistent distance

---

## Step 2: Generate the Podcast

```bash
uv run transcript podcast my-project my-video-name --voice voices/my-voice.wav
```

This will:
1. Read the podcast script from the previous step
2. Split it into chunks (the model processes short pieces at a time)
3. Send each chunk to Replicate with your voice sample
4. Download and stitch the audio together
5. Save the final episode as a `.wav` file

You will see progress printed for each chunk:

```
Synthesizing chunk 1/8...
Synthesizing chunk 2/8...
...
Podcast episode saved to: projects/my-project/output/my-video-name-podcast.wav
```

---

## Under the Hood: `tts.py`

Open `tts.py`. There are three functions working together:

### `_split_into_chunks(text)`

XTTS v2 has a limit of ~250 characters per request. This function splits the script into sentence-sized pieces that fit within that limit.

### `_fetch_audio(url)`

Replicate returns a URL pointing to the generated audio. This function downloads that audio and reads it into a NumPy array so we can combine chunks later.

### `synthesize_podcast(script_text, voice_sample_path, output_path)`

The main function. It:
1. Splits the script into chunks
2. Sends each chunk to Replicate with your voice sample
3. Concatenates all the audio arrays into one
4. Writes the final WAV file

---

## Listening to the Result

Open the `.wav` file in any audio player. Check:

- Does it sound like you?
- Is the pacing natural?
- Are there any words that sound garbled?

If something sounds off, the most common fixes are:
- **Better voice sample** — record in a quieter environment
- **Clean up the script** — remove abbreviations (write "for example" not "e.g.") and symbols (write "percent" not "%")

---

## You Built the Full Pipeline

Here is everything this project does, end to end:

```
YouTube URL
    --> download video          (yt-dlp)
    --> extract audio           (MoviePy)
    --> transcribe speech       (Whisper via Replicate)
    --> rewrite as podcast      (OpenAI GPT-4o-mini)
    --> synthesize in your voice (XTTS v2 via Replicate)
    --> podcast episode .wav
```

Drop a YouTube URL in `urls.txt`, run three commands, get a podcast episode in your own voice.

---

## Checkpoint

- [ ] I have a clean voice sample WAV file saved in `voices/`
- [ ] The podcast command ran and produced a `.wav` file
- [ ] I listened to the output and it sounds recognizably like me

---

Next: [What You Can Build Next](./step-08-whats-next.md)
