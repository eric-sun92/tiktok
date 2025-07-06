import os
import json
import requests
import openai
from dotenv import load_dotenv
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from tqdm import tqdm

# --- Load environment variables from .env ---
load_dotenv()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# --- Config ---
AUDIO_PATH = "audio.mp3"
LYRICS_JSON = "lyrics.json"
OUTPUT_VIDEO = "output_video.mp4"
RESOLUTION = (1080, 1920)
ARTIST = "Lana Del Rey"
SONG = "Summertime Sadness"

# --- Mood description for GPT ---
def get_mood(verse_lines):
    text = " ".join([line["text"] for line in verse_lines])
    prompt = (
        "Describe the mood, setting, and aesthetic of the following lyrics "
        "as a single search phrase I can use to find matching vertical background videos "
        "for a TikTok lyric video. Include TikTok-style words like 'aesthetic', 'pinterest vibe', etc.:\n\n"
        f"{text}\n\nSearch phrase:"
    )
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().lower()

# --- Pexels video search ---
def search_pexels_video(search_phrase):
    headers = {'Authorization': PEXELS_API_KEY}
    params = {
        'query': search_phrase,
        'orientation': 'portrait',
        'per_page': 1
    }
    res = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    data = res.json()
    if data.get("videos"):
        return data["videos"][0]["video_files"][0]["link"]
    return None

# --- Download video ---
def download_video(url, filename):
    r = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)
    return filename

# --- Build lyric + background clip ---
def build_verse_clip(verse, background_path):
    verse_start = verse[0]["start"]
    verse_end = verse[-1]["start"] + 1
    verse_duration = verse_end - verse_start
    print(f"Verse duration: {verse_duration:.2f}s")

    try:
        raw_bg = VideoFileClip(background_path)
        bg_clip = raw_bg.loop(duration=verse_duration).subclip(0, verse_duration).resize(height=1920)
    except Exception as e:
        print(f"Failed to load or resize background: {e}")
        return None

    full_verse_text = " ".join([w["text"] for w in verse])
    try:
        print(f"Rendering TextClip: {full_verse_text}")
        txt_clip = TextClip(
            full_verse_text,
            fontsize=40,
            color="white",
            size=RESOLUTION,
            method="caption",
            align="center"
        ).set_position(("center", "bottom")).set_duration(verse_duration)
    except Exception as e:
        print(f"TextClip failed: {e}")
        return None

    return CompositeVideoClip([bg_clip, txt_clip]).set_duration(verse_duration)

# --- Load lyrics ---
with open(LYRICS_JSON, "r") as f:
    verses = json.load(f)

video_clips = []

for i, verse in enumerate(tqdm(verses, desc="Processing verses")):
    try:
        mood = get_mood(verse)
        print(f"Verse {i+1} mood: {mood}")
        search_query = f"{ARTIST} {SONG} {mood}"
        video_url = search_pexels_video(search_query)

        if not video_url:
            print(f"No video found for: {search_query}, skipping verse.")
            continue

        bg_path = f"bg_{i}.mp4"
        download_video(video_url, bg_path)

        clip = build_verse_clip(verse, bg_path)
        if clip:
            video_clips.append(clip)
        else:
            print(f"Verse {i+1} skipped due to clip error.")

    except Exception as e:
        print(f"Error processing verse {i+1}: {e}")

# --- Final video render ---
if video_clips:
    print("Concatenating and exporting final video...")
    final = concatenate_videoclips(video_clips, method="compose")
    final = final.set_audio(AudioFileClip(AUDIO_PATH))
    final.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
else:
    print("No clips created. Exiting.")
