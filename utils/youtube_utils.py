from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi,TranscriptsDisabled
import os
from dotenv import load_dotenv
import yt_dlp

# Load environment variables
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

# Optional: path to cookies file (exported from browser)
COOKIES_FILE = "youtube.com_cookies.txt" 

def get_latest_video(channel_id):
    """Get the latest video ID from a channel."""
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=1,
        order="date"
    )
    response = request.execute()
    if response["items"]:
        return response["items"][0]["id"]["videoId"]
    return None

def get_videos_after_timestamp(channel_id, timestamp, max_results=50):
    """
    Get video IDs from a channel published after the specified timestamp.
    
    Args:
        channel_id (str): The YouTube channel ID
        timestamp (str): ISO 8601 timestamp format (e.g., '2023-01-01T00:00:00Z')
        max_results (int): Maximum number of videos to retrieve (default: 50)
    
    Returns:
        list: List of video IDs
    """
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        publishedAfter=timestamp,
        type="video"
    )
    
    try:
        response = request.execute()
        video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
        return video_ids
    except Exception as e:
        print(f"Error fetching videos for channel {channel_id}: {e}")
        return []

def get_video_title_and_publishdate(video_id):
    """Get the title of a video by its ID."""
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        if response["items"]:
            return response["items"][0]["snippet"]["title"], response["items"][0]["snippet"]["publishedAt"]
        return None,None
    except Exception as e:
        print(f"Error fetching title for video {video_id}: {e}")
        return None,None

def download_subtitles(video_id, languages=["zh-Hans","zh-TW", "en","zh"]):
    """Download subtitles for a given video ID, trying multiple languages."""
    print(f"start subtitles downloaded for video {video_id}")
    try:
        # Create an instance of YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        # Call fetch on the instance
        transcript = ytt_api.fetch(video_id=video_id, languages=languages)
        subtitle_content = ""
        for snippet in transcript.snippets:
            subtitle_content = subtitle_content + snippet.text + '\n'
        print(f"finish subtitles downloaded for video {video_id}")
        return subtitle_content
    except TranscriptsDisabled:
        print(f"Subtitles are disabled for this video {video_id}")
        return "SUBTITLE_DISABLED"
    except Exception as e:
        print(f"YouTubeTranscriptApi Error downloading subtitles for {video_id}: {e}")
    # 2️⃣ Fallback to yt-dlp
    try:
        print(f"[yt-dlp] Trying to fetch subtitles for {video_id}...")
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": languages,
            "subtitlesformat": "vtt",
            "quiet": True,
            "outtmpl": f"{video_id}.%(ext)s"
        }
        if COOKIES_FILE and os.path.exists(COOKIES_FILE):
            ydl_opts["cookiefile"] = COOKIES_FILE

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            # Download subs to file
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        # Find the .vtt file and read it
        vtt_file = f"{video_id}.vtt"
        if os.path.exists(vtt_file):
            with open(vtt_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # Filter out timestamps and metadata
            subtitle_content = "\n".join(line.strip() for line in lines if line.strip() and not line.strip().isdigit() and "-->" not in line)
            os.remove(vtt_file)  # Clean up
            print(f"[yt-dlp] Subtitles downloaded for {video_id}")
            return subtitle_content
        else:
            print(f"[yt-dlp] No .vtt file found for {video_id}")
            return None

    except Exception as e:
        print(f"[yt-dlp] Error fetching subtitles for {video_id}: {e}")
        return None    

def download_subtitles_to_file(video_id, output_dir="subtitles", languages=["zh-Hans", "en"]):
    """Download subtitles for a given video ID, trying multiple languages."""
    try:
        # Create an instance of YouTubeTranscriptApi
        ytt_api = YouTubeTranscriptApi()
        # Call fetch on the instance
        transcript = ytt_api.fetch(video_id=video_id, languages=languages)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        subtitle_file = os.path.join(output_dir, f"{video_id}.txt")
        with open(subtitle_file, "w", encoding="utf-8") as f:
            for snippet in transcript.snippets:
                f.write(f"{snippet.text}\n")
        print(f"Subtitles downloaded for video {video_id} ")
        return subtitle_file
    except Exception as e:
        print(f"Error downloading subtitles for {video_id}: {e}")
        return None