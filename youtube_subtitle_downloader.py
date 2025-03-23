import re
import os
from utils.youtube_utils import get_latest_video, get_video_title_and_publishdate, download_subtitles, get_videos_after_timestamp
from utils.gemini_utiles import generate_content
from datetime import datetime, timedelta
from utils.postgreSQL_utils import save_summary, get_latest_video_timestamp


#Go to the YouTube channel page，Right-click the page > View Page Source , Search for channel_id
channel_infos = {
        "又大又好又便宜":"UCKi9Gr3yA1gxfLt15_wbsSA",
        "老汤美股财经":"UCeTEWFsNC3eeUsn9hvsDALQ",
        "X-invest 想法":"UCON-3EaYE-VXoAhYokZhodw",
        "美股咖啡馆":"UCjrP2TtSTifuRJ76hW2IW1A"}

def main():     
    """
    Main function that iterates through the channel information and processes each YouTube channel.
    Prints channel information and initiates the processing of each channel's videos.
    """
    print(channel_infos)
    for channel_name,channel_id in channel_infos.items():
        print(channel_id,channel_name)
        process_youbute(channel_id,channel_name)
        

def process_youbute(channel_id, channel_name):
    """
    Processes videos from a specific YouTube channel.
    
    Args:
        channel_id (str): The YouTube channel ID to process
        channel_name (str): The name of the YouTube channel
        
    Retrieves the latest video timestamp from the database and processes any new videos
    that have been uploaded since the last check.
    """
    print(f"Processing channel: {channel_id}")
    latest_video_timestamp = get_latest_video_timestamp(channel_name)
    if not latest_video_timestamp:
        print(f"No latest video timestamp found for channel {channel_id}")
        return
    print(f"Latest video timestamp: {latest_video_timestamp}")
    
    # 将时间戳转换为 RFC 3339 格式，并添加1分钟
    dt = datetime.fromisoformat(str(latest_video_timestamp))
    dt = dt + timedelta(minutes=1)  # Add 1 minute
    formatted_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
    video_id_list = get_videos_after_timestamp(channel_id, formatted_timestamp)
    if not video_id_list:
        print(f"No recent video found for channel {channel_id}")
        return
    for video_id in video_id_list: 
        process_video(video_id,channel_name)   
    
def process_video(video_id,channel_name):
    """
    Processes a single YouTube video by downloading its subtitles and generating a summary.
    
    Args:
        video_id (str): The YouTube video ID to process
        
    Downloads video metadata and subtitles, generates a summary using Gemini,
    and optionally saves the summary to the database.
    """
    video_title, published_at = get_video_title_and_publishdate(video_id)
    if not video_title:
        print(f"Failed to get video title for video {video_id}")
        return

    print(f"Latest video title: {video_title}")
    subtitle_content = download_subtitles(video_id)

    if not subtitle_content:
        print(f"Failed to download subtitles for video {video_title}")
        return
    
    # Convert string to datetime if it's a string
    video_published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00')) if published_at else datetime.now()
    # Format the datetime as ISO 8601 format with UTC timezone
    formatted_date = video_published_at.strftime('%Y-%m-%dT%H:%M:%SZ')
    summary = generate_content(subtitle_content)
        
    if not summary:
        print(f"Failed to generate summary for video {video_id}")
        return

    print(f"Summary: {summary}")
    save_summary(video_id, video_title, "todo", formatted_date, channel_name)
    save_to_file(video_id=video_id,channel_name=channel_name, transcript=summary)
    
def save_to_file(video_id,channel_name, transcript, output_dir="subtitles"):
    subtitle_file = os.path.join(output_dir, f"{channel_name}_{video_id}.txt")
    with open(subtitle_file, "w", encoding="utf-8") as f:
        for entry in transcript:
            f.write(f"{entry}")
    print(f"Subtitles downloaded for video {video_id}")

if __name__ == "__main__":
    main()
    # process_video("ZGy7hWdRMK0")