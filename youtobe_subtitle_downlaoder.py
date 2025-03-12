from youtube_utils import get_latest_video, get_video_title, download_subtitles
from mongodb_utils import init_mongodb, save_to_mongodb

def main():
    # Initialize MongoDB connection
    if not init_mongodb():
        print("Failed to connect to MongoDB")
        return

    channel_ids = ["UCeTEWFsNC3eeUsn9hvsDALQ"]
    print(channel_ids)
    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        video_id = get_latest_video(channel_id)
        if not video_id:
            print(f"No recent video found for channel {channel_id}")
            continue
        
        video_title = get_video_title(video_id)
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

if __name__ == "__main__":
    main()