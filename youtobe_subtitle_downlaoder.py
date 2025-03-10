from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')
# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)


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

def get_video_title(youtube, video_id):
    """Get the title of a video by its ID."""
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        if response["items"]:
            return response["items"][0]["snippet"]["title"]
        return None
    except Exception as e:
        print(f"Error fetching title for video {video_id}: {e}")
        return None

def download_subtitles(video_id, output_dir="subtitles", languages=["zh-Hans", "en"]):
    """Download subtitles for a given video ID, trying multiple languages."""
    try:
        # Try fetching transcript in specified languages
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        subtitle_file = os.path.join(output_dir, f"{video_id}.txt")
        with open(subtitle_file, "w", encoding="utf-8") as f:
            for entry in transcript:
                f.write(f"{entry['start']} - {entry['text']}\n")
        print(f"Subtitles downloaded for video {video_id} in {transcript[0]['lang']}")
        return subtitle_file
    except Exception as e:
        print(f"Error downloading subtitles for {video_id}: {e}")
        return None

def main():
    channel_ids = ["UCeTEWFsNC3eeUsn9hvsDALQ"]
    print(channel_ids)
    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        video_id = get_latest_video(channel_id)
        if video_id:
            video_title=get_video_title(youtube, video_id)
            if video_title:
                print(f"Latest video title: {video_title}")
            else:
                print(f"Failed to get video title for video {video_id}")    
                
            subtitle_file = download_subtitles(video_id)
            if subtitle_file:
                print(f"Subtitles saved to: {subtitle_file}")
        else:
            print(f"No recent video found for channel {channel_id}")

if __name__ == "__main__":
    main()