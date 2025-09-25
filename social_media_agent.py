
# --------------------------------------------------------------
# Step 0: Import packages and modules
# --------------------------------------------------------------
import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from agents import Agent, WebSearchTool, function_tool, trace
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List


# --------------------------------------------------------------
# Step 1: Get OpenAI API key
# --------------------------------------------------------------
load_dotenv()

# --------------------------------------------------------------
# Step 2: Define tools for agent
# --------------------------------------------------------------

# Tool: Generate social media content from transcript
@function_tool
def generate_content(video_transcript: str, social_media_platform: str):
    print(f"Generating social media content for {social_media_platform}...")

    # Initialize OpenAI client with API key fetched at call-time
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set. Please provide it in the UI or environment.")
    client = OpenAI(api_key=api_key)

    # Generate content

    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "user", "content": f"Here is a new video transcript:\n{video_transcript}\n\n"
                                        f"Generate a social media post on my {social_media_platform} based on my provided video transcript.\n"}
        ],
        max_output_tokens=2500  # Increase tokens for longer blog posts
    )

    return response.output_text


# --------------------------------------------------------------
# Step 3: Define agent (content writer agent)
# --------------------------------------------------------------

@dataclass
class Post:
    platform: str
    content: str


content_writer_agent = Agent(name="Content Writer Agent")


# --------------------------------------------------------------
# Step 4: Define helper functions and adapters for app.py
# --------------------------------------------------------------

# Fetch transcript from a youtube video using the video id
def get_transcript(video_id: str, languages: list = None) -> str:
    """
    Retrieves the transcript for a YouTube video.

    Args:
        video_id (str): The YouTube video ID.
        languages (list, optional): List of language codes to try, in order of preference.
                                   Defaults to ["en"] if None.

    Returns:
        str: The concatenated transcript text.

    Raises:
        Exception: If transcript retrieval fails, with details about the failure.
    """
    if languages is None:
        languages = ["en"]

    try:
        # Use the Youtube transcript API
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id, languages=languages)

        # More efficient way to concatenate all text snippets
        transcript_text = " ".join(snippet.text for snippet in fetched_transcript)

        return transcript_text

    except Exception as e:
        # Handle specific YouTube transcript API exceptions
        from youtube_transcript_api._errors import (
            CouldNotRetrieveTranscript, 
            VideoUnavailable,
            InvalidVideoId, 
            NoTranscriptFound,
            TranscriptsDisabled
        )

        if isinstance(e, NoTranscriptFound):
            error_msg = f"No transcript found for video {video_id} in languages: {languages}"
        elif isinstance(e, VideoUnavailable):
            error_msg = f"Video {video_id} is unavailable"
        elif isinstance(e, InvalidVideoId):
            error_msg = f"Invalid video ID: {video_id}"
        elif isinstance(e, TranscriptsDisabled):
            error_msg = f"Transcripts are disabled for video {video_id}"
        elif isinstance(e, CouldNotRetrieveTranscript):
            error_msg = f"Could not retrieve transcript: {str(e)}"
        else:
            error_msg = f"An unexpected error occurred: {str(e)}"

        print(f"Error: {error_msg}")
        raise Exception(error_msg) from e


# Extract platforms from the constructed user message in app.py
def _extract_platforms_from_message(message: str) -> List[str]:
    wanted = []
    for name in ["LinkedIn", "Instagram", "Twitter"]:
        if name.lower() in (message or "").lower():
            wanted.append(name)
    # Fallback: if nothing was detected, default to LinkedIn
    return wanted or ["LinkedIn"]


# Result object expected by app.py (it accesses result.new_items)
class _Result:
    def __init__(self, posts: List[Post]):
        # Store items in a simple structure compatible with ItemHelpers below
        self.new_items = [
            {"platform": p.platform, "content": p.content} for p in posts
        ]


# Provide a Runner with an async run(...) API expected by app.py
class Runner:
    @staticmethod
    async def run(agent: Agent, input_items: List[dict]) -> _Result:
        # app.py sends a single user item with the full message including transcript and platforms
        message = (input_items or [{}])[0].get("content", "")

        # Heuristically separate transcript from message (it includes "transcript: ...")
        # We pass the entire message as transcript to the tool if we can't split reliably.
        transcript_text = message
        if "transcript:" in message.lower():
            # split on the first occurrence of "transcript:" to get the tail content
            lower_msg = message.lower()
            idx = lower_msg.find("transcript:")
            transcript_text = message[idx + len("transcript:") :].strip()

        platforms = _extract_platforms_from_message(message)

        posts: List[Post] = []
        for platform in platforms:
            try:
                content_text = generate_content(transcript_text, platform)
            except Exception as e:
                content_text = f"Error generating content for {platform}: {e}"
            posts.append(Post(platform=platform, content=content_text))

        return _Result(posts)


# Extend ItemHelpers with the method used by app.py
class ItemHelpers:
    @staticmethod
    def text_message_outputs(new_items: List[dict]) -> str:
        # app.py expects a JSON string with a key "response" that is a list
        # of { platform, content }
        import json as _json
        payload = {
            "response": [
                {"platform": it.get("platform", "Unknown"), "content": it.get("content", "")} 
                for it in (new_items or [])
            ]
        }
        return _json.dumps(payload)



# --------------------------------------------------------------
# Step 5: Run the agent
# --------------------------------------------------------------
async def main():
    video_id = "OZ5OZZZ2cvk"
    transcript = get_transcript(video_id)

    msg = f"Generate a LinkedIn post and an Instagram caption based on this video transcript: {transcript}"

    # Package input for the agent
    input_items = [{"content": msg, "role": "user"}]

    # Run content writer agent
    # Add trace to see the agent's execution steps
    # You can check the trace on https://platform.openai.com/traces
    with trace("Writing content"):
        result = await Runner.run(content_writer_agent, input_items)
        output = ItemHelpers.text_message_outputs(result.new_items)
        print("Generated Post:\n", output)

if __name__ == "__main__":
    asyncio.run(main())







