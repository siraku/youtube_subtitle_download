# import re
import os
# from time import sleep
import signal
import sys
from utils.youtube_utils import get_latest_video, get_video_title_and_publishdate, download_subtitles, get_videos_after_timestamp
from utils.gemini_utiles import generate_content
from datetime import datetime, timedelta
# from utils.mongodb_utils import save_to_mongodb
from utils.postgreSQL_utils import get_youtube_channels_info,update_youbute_channel_process_date,save_video_info_for_download


# Timeout handler function
def timeout_handler(signum, frame):
    print("\nExecution timed out after 30 minutes. Terminating program.")
    sys.exit(1)


#Go to the YouTube channel page，Right-click the page > View Page Source , Search for channelid
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
    # Set 30-minute timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30 * 60)  # 30 minutes in seconds
    
    try:
        subscribed_channels=get_youtube_channels_info()
        for channel_info in subscribed_channels:
            print("**************************************************************************")
            print("Start process channel: "+channel_info['channel_name']+" last update time: "+channel_info['update_time'].strftime('%Y-%m-%d %H:%M:%S'))
            process_youbute(channel_info)
            update_youbute_channel_process_date(channel_info,datetime.now())
    finally:
        # Disable the alarm when done
        signal.alarm(0)


def process_youbute(channel_info: dict):
    """
    Processes videos from a specific YouTube channel.
    
    Args:
        channel_id (str): The YouTube channel ID to process
        channel_name (str): The name of the YouTube channel
        
    Retrieves the latest video timestamp from the database and processes any new videos
    that have been uploaded since the last check.
    """
    latest_video_timestamp = channel_info['update_time']
    channel_id=channel_info['channel_id']
    
    # if latest_video_timestamp is not before today, then return 
    if latest_video_timestamp.date() == datetime.now().date():
        print("Update date is today, no need to update "+channel_info['channel_name'])
        return


    # 将时间戳转换为 RFC 3339 格式，并添加1分钟
    dt = datetime.fromisoformat(str(latest_video_timestamp))
    dt = dt + timedelta(minutes=1)  # Add 1 minute
    formatted_timestamp = dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
    video_id_list = get_videos_after_timestamp(channel_id, formatted_timestamp)
    if not video_id_list:
        print(f"No recent video found for channel {channel_id}")
        return
    for video_id in video_id_list: 
        # process_video(video_id)   
        print("Start process video: "+video_id)
        process_video(video_id,channel_info)
    
def process_video(video_id,channel_info: dict):
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

    print(f"video title: {video_title}")
    subtitle_content = download_subtitles(video_id)

    if not subtitle_content:
        print(f"Failed to download subtitles for video {video_title}")
        return
    if subtitle_content == "SUBTITLE_DISABLED":
        print(f"Subtitles are disabled for video {video_title}, channel name: {channel_info['channel_name']},save to db")
        save_video_info_for_download(channel_info['channel_name'],video_id)
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

    # save raw data and summary to file
    save_to_file(video_date=formatted_date,channel_name=channel_info['channel_name'], video_id=video_id,transcript=subtitle_content,summary=summary)

    # save_summary(video_id, video_title, "todo", formatted_date, channel_name)
    # save_to_mongodb(video_id, video_title, channel_name, summary, formatted_date)
    # save_to_file(video_id=video_id,channel_name=channel_name, transcript=summary)
    
def save_to_file(video_date,channel_name, video_id,transcript,summary):
    # Use absolute paths instead of relative paths
    base_dir = "/Users/siraku/Desktop/git/youtube-summarize"
    transcript_base_dir = os.path.join(base_dir, "subtitles/transcript")
    summary_base_dir = os.path.join(base_dir, "subtitles/summary")

    subtitle_file = os.path.join(transcript_base_dir, f"{channel_name}_{video_date}_{video_id}.txt")
    with open(subtitle_file, "w", encoding="utf-8") as f:
        f.write(f"{transcript}")

    summary_file= os.path.join(summary_base_dir, f"{channel_name}_{video_date}_{video_id}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"{summary}")
        
    print("Save to file completed")

if __name__ == "__main__":
    main()