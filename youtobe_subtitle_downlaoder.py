from youtube_utils import get_latest_video, get_video_title_and_publishdate, download_subtitles
from gemini_utiles import generate_content
from video_data import VideoData
from datetime import datetime
from postgreSQL_utils import save_summary


def main():
        
#Go to the YouTube channel page，Right-click the page > View Page Source , Search for channel_id
# 老汤美股财经 UCeTEWFsNC3eeUsn9hvsDALQ  又大又好又便宜 UCKi9Gr3yA1gxfLt15_wbsSA  X-invest 想法 UCON-3EaYE-VXoAhYokZhodw
    channel_ids = ["UCKi9Gr3yA1gxfLt15_wbsSA"]
    print(channel_ids)
    for channel_id in channel_ids:
        print(f"Processing channel: {channel_id}")
        video_id = get_latest_video(channel_id)
        if not video_id:
            print(f"No recent video found for channel {channel_id}")
            continue
        
        video_title, published_at = get_video_title_and_publishdate(video_id)
        if not video_title:
            print(f"Failed to get video title for video {video_id}")
            continue

        print(f"Latest video title: {video_title}")
        subtitle_content = download_subtitles(video_id)

        if not subtitle_content:
            print(f"Failed to download subtitles for video {video_title}")
            continue

        # Ensure published_at is a datetime object
        
        # Convert string to datetime if it's a string
        video_published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00')) if published_at else datetime.now()
        timestamp = video_published_at.timestamp()

        video_data = VideoData(
            video_id=video_id,
            video_title=video_title,
            subtitle_content=subtitle_content,
            published_at=video_published_at
        )
        summary = generate_content(video_data.subtitle_content)
        
        if not summary:
            print(f"Failed to generate summary for video {video_id}")
            continue

        print(f"Summary: {summary}")
        save_summary(video_id, video_title, summary, timestamp, "又大又好又便宜")
            

if __name__ == "__main__":
    main()