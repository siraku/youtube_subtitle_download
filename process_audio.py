import re
import os
from time import sleep
import yt_dlp
import whisper
from datetime import datetime
from utils.gemini_utiles import generate_content
from utils.postgreSQL_utils import get_video_info_for_download,delete_video_info_for_download

def download_audio(url,channel_name,video_id):
    audio_output_path = "subtitles/audio/" + channel_name + "_" + video_id
    ydl_opts = {
        'format': 'bestaudio/best',      # best available audio
        'outtmpl': audio_output_path,          # output file template
        'postprocessors': [{             # convert to mp3
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',   # kbps
        }],
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return audio_output_path + ".mp3"

def convert_audio_to_text(audio_file_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_file_path)
    # with open("transcript.txt", "w", encoding="utf-8") as f:
    #     # Convert result to string if it's not already
    #     text_content = str(result["text"]) if isinstance(result["text"], list) else result["text"]
    #     f.write(text_content)
    # print("Transcription saved to transcript.txt")
    
    text_content = str(result["text"]) if isinstance(result["text"], list) else result["text"]
    summary = generate_content(text_content)
    print(summary)
    return summary

def save_content_summary(channel_name, video_id, content_summary):
    # Use absolute paths instead of relative paths
    base_dir = "/Users/siraku/Desktop/git/youtube-summarize"
    summary_base_dir = os.path.join(base_dir, "subtitles/summary")
    date = datetime.now().strftime("%Y%m%d")
    summary_file= os.path.join(summary_base_dir, f"{channel_name}_{date}_{video_id}.md")
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"{content_summary}")
        
    print("Save to file completed")

if __name__ == "__main__":
    audio_download_list = get_video_info_for_download()
    for audio_download in audio_download_list:
        channel_name = audio_download['channel_name']
        video_id = audio_download['video_id']
        print("start process", channel_name, video_id)
        # Example video URL
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        audio_output_path = download_audio(video_url,channel_name,video_id)
        sleep(1)
        print(audio_output_path)
        content_summary = convert_audio_to_text(audio_output_path)
        save_content_summary(channel_name, video_id, content_summary)
        print("delete delete downloaded video info")
        delete_video_info_for_download(video_id)
        print("delete completed")
