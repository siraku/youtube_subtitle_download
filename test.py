from utils.postgreSQL_utils import  get_latest_video_timestamp, get_youtube_channels_info
from utils.youtube_utils import get_videos_after_timestamp

# Example usage
# save_summary(
#     video_id="abc123",
#     title="Sample Video",
#     video_content_summary="This is the summary text",
#     video_timestamp="2024-03-15 14:30:00",
#     author="John Doe"
# )

# latest_video_timestamp = get_latest_video_timestamp("又大又好又便宜")
# print(latest_video_timestamp)

# Example usage
# timestamp = "2025-05-01T00:00:00Z"
# video_ids = get_videos_after_timestamp("UCKi9Gr3yA1gxfLt15_wbsSA", timestamp)
# print(video_ids)


result=get_youtube_channels_info() 
for item in result:
    print(item['channel_id'],item['channel_name'],item['update_time'])

