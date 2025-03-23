from pymongo import MongoClient
from pymongo import server_api
import certifi
import os
import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
URI = os.getenv('MongoDB_URI')

# Initialize MongoDB client
client = MongoClient(
    URI,
    server_api=server_api.ServerApi('1'),
    tlsCAFile=certifi.where()
)
db = client['youtube_data']
videos_collection = db['videos']

def init_mongodb():
    """Initialize MongoDB connection and test it."""
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(e)
        return False

def save_to_mongodb(video_id, title, subtitle_content):
    """Save video data to MongoDB."""
    try:
        jst = pytz.timezone('Asia/Tokyo')
        video_data = {
            'video_id': video_id,
            'title': title,
            'subtitles': subtitle_content,
            'created_at': datetime.datetime.now(jst)
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