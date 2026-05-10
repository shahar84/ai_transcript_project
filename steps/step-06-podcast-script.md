# Step 6: Writing the Podcast Script with AI

## What We're Building

You have a raw transcript — but a transcript reads like a conversation, full of filler words, interruptions, and unfinished thoughts. A podcast episode needs to sound different: clear, engaging, structured.

In this step we send the transcript to OpenAI and ask it to rewrite the content as a polished podcast monologue — a single speaker who explains the key ideas in a natural, flowing way.

```
transcript .txt  -->  OpenAI GPT-4o-mini  -->  podcast script .txt
```

---

## Get an OpenAI API Key

1. Sign up at https://platform.openai.com
2. Go to API keys and create a new key
3. Add it to your `.env` file:

```
OPENAI_API_KEY=sk-...
```

We use **gpt-4o-mini** — it is fast, cheap, and more than capable for rewriting text. A typical transcript costs a fraction of a cent to process.

---

## The Code: `llm.py`

Open `llm.py`. There are two functions:

### `generate_podcast_script(transcript_text)`

Sends the transcript to OpenAI with a system prompt that instructs the model to act as a podcast script writer:

```python
_SYSTEM_PROMPT = (
    "You are a podcast script writer. Transform the provided transcript into an engaging "
    "monologue for a single speaker. Use a conversational, warm tone. Keep the key insights "
    "but make them flow naturally when spoken aloud. Aim for 3-5 minutes of speaking time "
    "(roughly 450-750 words). Start with a hook that draws the listener in. End with a clear "
    "takeaway. Write continuous flowing speech — no bullet points, headers, or lists."
)
```

The system prompt is the most important part. It shapes everything about what the model produces. Notice:
- "single speaker" — we want a monologue, not a dialogue
- "no bullet points, headers, or lists" — the output will be read aloud, so formatting would sound broken
- word count guidance — keeps the episode a reasonable length

### `save_script(script_text, video_name, output_folder)`

Saves the script as `video-name-podcast-script.txt` in the project's output folder.

---

## The New CLI Command

```bash
uv run transcript script my-project my-video
```

This reads the `.txt` transcript from the project's output folder and writes the podcast script next to it.

Try it:

```bash
# First make sure the video is already transcribed
uv run transcript run my-project

# Then generate the podcast script
uv run transcript script my-project my-video-name
```

Open the resulting `-podcast-script.txt` file. Read it aloud. Does it sound natural? Does it flow?

---

## Understanding the Prompt

The system prompt is a set of instructions the model follows every time. The user message is the actual content — the transcript.

Try changing the system prompt in `llm.py` and re-running:

- Ask for a **two-minute summary** instead of five minutes
- Ask for a **more formal, BBC documentary tone**
- Ask it to **start with a provocative question**

Each change produces a completely different script from the same transcript. This is prompt engineering — and it is one of the most valuable skills you can develop right now.

---

## What Makes a Good Podcast Script?

A good script for text-to-speech (which we use in Step 7) has these qualities:

- **No abbreviations** — write "for example" not "e.g.", "that is" not "i.e."
- **No symbols** — write "percent" not "%", "dollars" not "$"
- **Short sentences** — easier to speak and easier to follow
- **Natural pauses** — periods and commas become pauses in TTS output

If the generated script has any of the above issues, fix them before moving to Step 7.

---

## Checkpoint

- [ ] My `OPENAI_API_KEY` is in `.env` and the command runs without errors
- [ ] I have a `-podcast-script.txt` file in the project output folder
- [ ] I read the script aloud and it sounds natural
- [ ] I understand what the system prompt does and tried at least one change

---

Next: [Step 7 - Generating Your Podcast Audio](./step-07-podcast-audio.md)
