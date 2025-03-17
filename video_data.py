from dataclasses import dataclass
from datetime import datetime

@dataclass
class VideoData:
    video_id: str
    video_title: str
    subtitle_content: str
    published_at: datetime