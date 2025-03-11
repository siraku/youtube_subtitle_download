from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo import server_api
import certifi

# Load environment variables
load_dotenv()
# Get API key from environment variable
API_KEY = os.getenv('YOUTUBE_API_KEY')
URI=os.getenv('MongoDB_URI')

# Initialize MongoDB client with SSL certificate verification
client = MongoClient(
    URI,
    server_api=server_api.ServerApi('1'),
    tlsCAFile=certifi.where()  # Add this line to use proper SSL certificates
)
db = client['youtube_data']
videos_collection = db['videos']

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Initialize YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def save_to_mongodb(video_id, title, subtitle_content):
    """Save video data to MongoDB."""
    try:
        video_data = {
            'video_id': video_id,
            'title': title,
            'subtitles': subtitle_content,
        }
        videos_collection.update_one(
            {'video_id': video_id},
            {'$set': video_data},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving to MongoDB: {e}")
        return False

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

def download_subtitles_to_file(video_id, output_dir="subtitles", languages=["zh-Hans", "en"]):
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

def download_subtitles(video_id, output_dir="subtitles", languages=["zh-Hans", "en"]):
    """Download subtitles for a given video ID, trying multiple languages."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        subtitle_content = []
        for entry in transcript:
            subtitle_content.append({
                'start': entry['start'],
                'text': entry['text']
            })
            
        print(f"Subtitles downloaded for video {video_id}")
        return subtitle_content
    except Exception as e:
        print(f"Error downloading subtitles for {video_id}: {e}")
        return None, None

def main():
    channel_ids = ["UCeTEWFsNC3eeUsn9hvsDALQ"]
    print(channel_ids)
    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        video_id = get_latest_video(channel_id)
        if video_id:
            video_title = get_video_title(youtube, video_id)
            if video_title:
                print(f"Latest video title: {video_title}")
                subtitle_content = download_subtitles(video_id)
                if subtitle_content:
                    if save_to_mongodb(video_id, video_title, subtitle_content):
                        print(f"Video data saved to MongoDB")
                    else:
                        print(f"Failed to save video data to MongoDB")
            else:
                print(f"Failed to get video title for video {video_id}")
        else:
            print(f"No recent video found for channel {channel_id}")

if __name__ == "__main__":
    main()