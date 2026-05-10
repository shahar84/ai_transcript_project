# Step 5: Generating a Podcast Script with OpenAI
#
# You have transcripts. Now we use OpenAI to rewrite them into
# a single, polished podcast script.
#
# The key idea: a raw transcript is messy — filler words, incomplete
# sentences, no structure. A language model can transform it into
# something that sounds natural when read aloud.
#
# This script reads all .txt files from a project's transcripts/ folder,
# combines them, and sends them to GPT-4o-mini with a system prompt
# that tells it how to write for a podcast.
#
# Run: uv run examples/step5_podcast_script.py

from pathlib import Path
from openai import OpenAI
from config import settings

PROJECT_NAME = "my-first-project"
PROJECTS_DIR = Path("projects")

# --- Part 1: Load all transcripts ---
transcripts_dir = PROJECTS_DIR / PROJECT_NAME / "transcripts"

txt_files = sorted(transcripts_dir.glob("*.txt"))
if not txt_files:
    print(f"No transcripts found in {transcripts_dir}")
    print(f"Run 'uv run transcript run {PROJECT_NAME}' first.")
    exit()

print(f"Found {len(txt_files)} transcript(s):")
for f in txt_files:
    print(f"  {f.name}")

combined_transcript = "\n\n".join(f.read_text(encoding="utf-8") for f in txt_files)

# --- Part 2: Define the system prompt ---
# The system prompt sets the role and constraints for the model.
# This is what shapes the output — try editing it and see what changes.

SYSTEM_PROMPT = (
    "You are a podcast script writer. Transform the provided transcript into an engaging "
    "monologue for a single speaker. Use a conversational, warm tone. Keep the key insights "
    "but make them flow naturally when spoken aloud. Aim for 3-5 minutes of speaking time "
    "(roughly 450-750 words). Start with a hook that draws the listener in. End with a clear "
    "takeaway. Write continuous flowing speech — no bullet points, headers, or lists."
)

# --- Part 3: Call the OpenAI API ---
print("\nGenerating podcast script...")

client = OpenAI(api_key=settings.OPENAI_API_KEY)
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Here is the transcript:\n\n{combined_transcript}"},
    ],
)

script_text = response.choices[0].message.content

# --- Part 4: Save the script ---
podcast_dir = PROJECTS_DIR / PROJECT_NAME / "podcast"
podcast_dir.mkdir(parents=True, exist_ok=True)
script_path = podcast_dir / "script.txt"
script_path.write_text(script_text, encoding="utf-8")

print(f"Script saved to: {script_path}")
print(f"\nFirst 200 characters:\n{script_text[:200]}...")
print("\nThis is exactly what the CLI does. Try it yourself:")
print(f"  uv run transcript script {PROJECT_NAME}")
