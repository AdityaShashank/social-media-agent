# social_media_agent.py

import os
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN not found. Please set it in your .env file.")

# Initialize GitHub-hosted OpenAI client
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=GITHUB_TOKEN,
)

def summarize_transcript_local(transcript: str) -> str:
    # Since you removed BART and transformers, this is a stub that returns the transcript itself
    # You can later integrate a faster summarization method or OpenAI API here
    print("[TRACE] Summarizing transcript (currently passthrough)...")
    return transcript.strip()

def generate_social_media_content_gpt4o(summary: str, platform: str) -> str:
    print(f"[TRACE] Generating social media content for {platform} using GitHub GPT-4o...")
    prompt = (
        f"Here is a summary of a YouTube video transcript:\n{summary}\n\n"
        f"Please generate a social media post for {platform} based on this summary.\n"
        "Include relevant hashtags and a call to action."
    )

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional social media assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300,
        top_p=1
    )

    return response.choices[0].message.content.strip()

def fetch_youtube_transcript(video_url: str) -> str:
    try:
        video_id = video_url.split("v=")[-1].split("&")[0]
        print(f"[DEBUG] Using video ID: {video_id}")

        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        try:
            transcript = transcripts.find_manually_created_transcript(['en'])
            print("[DEBUG] Found manually created transcript.")
        except Exception as e_manual:
            print(f"[DEBUG] No manually created transcript: {e_manual}")
            try:
                transcript = transcripts.find_generated_transcript(['en'])
                print("[DEBUG] Found generated transcript.")
            except Exception as e_generated:
                error_msg = f"Could not find any transcript: manual error: {e_manual}, generated error: {e_generated}"
                print(f"[ERROR] {error_msg}")
                return error_msg

        try:
            entries = transcript.fetch()
            # Do not try to convert to list, just iterate as before
            if not entries:
                print("[ERROR] Transcript fetch returned empty.")
                return "Error fetching transcript: Transcript is empty."
            full_text = " ".join(entry.text for entry in entries)
            return full_text
        except Exception as e_fetch:
            print(f"[ERROR] Exception while fetching transcript entries: {e_fetch}")
            return f"Error fetching transcript: {e_fetch}"

    except Exception as e:
        print(f"[ERROR] Exception while fetching transcript: {e}")
        return f"Error fetching transcript: {e}"


def main():
    video_url = input("Enter a YouTube video URL: ").strip()
    transcript = fetch_youtube_transcript(video_url)

    if transcript.startswith("Error fetching transcript"):
        print(transcript)
        return

    platform = input("Enter the social media platform (e.g., Linkedin, Twitter, Facebook): ").strip()

    summarized_transcript = summarize_transcript_local(transcript)
    print("[DEBUG] Summarized Transcript:\n", summarized_transcript)

    post = generate_social_media_content_gpt4o(summarized_transcript, platform)
    print(f"\nGenerated Social Media Post for {platform}:\n{post}")

if __name__ == "__main__":
    main()
