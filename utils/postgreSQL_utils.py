from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv('POSTGRESQL_CONNECTION_USER')
PASSWORD = os.getenv('POSTGRESQL_CONNECTION_PW')

# Use psycopg2 instead of asyncpg for synchronous operations
DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@ep-twilight-hall-a1y1uxar-pooler.ap-southeast-1.aws.neon.tech/ai-kids-story?sslmode=require"

# Create engine
engine = create_engine(DATABASE_URL)

def get_youtube_channels_info() -> List[Dict]:
    """Retrieve all YouTube channels information from the database"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT channel_id,channel_name, update_time
                FROM youtube.youtube_subscribed_channel 
                WHERE flag = TRUE
            """)
            result = conn.execute(query).fetchall()
            return [{'channel_id': row[0],'channel_name':row[1], 'update_time': row[2]} for row in result]
    except Exception as e:
        print(f"Error retrieving YouTube channels info: {e}")
        return []

def update_youbute_channel_process_date(channel_info: dict,today) -> bool:
    """Update the process date for a YouTube channel"""
    try:
        with engine.connect() as conn:
            query = text("""
                UPDATE youtube.youtube_subscribed_channel
                SET update_time = :update_time
                WHERE channel_id = :channel_id
            """)
            conn.execute(query, {
                'update_time': today,
                'channel_id': channel_info['channel_id']
            })
            conn.commit()
            return True
    except Exception as e:
        print(f"Error updating YouTube channel process date: {e}")
        return False

def get_summary_by_video_id(video_id: str) -> Optional[Dict]:
    """Retrieve a summary by video_id"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT video_id, title, video_content_summary, video_timestamp, author
                FROM youtube.youtube_subtitles_summary
                WHERE video_id = :video_id
            """)
            result = conn.execute(query, {'video_id': video_id}).fetchone()
            if result:
                return {
                    'video_id': result[0],
                    'title': result[1],
                    'video_content_summary': result[2],
                    'video_timestamp': result[3],
                    'author': result[4]
                }
        return None
    except Exception as e:
        print(f"Error retrieving summary: {e}")
        return None

def get_latest_video_timestamp(author:str) -> Optional[str]:
    """Retrieve the latest video_timestamp from the database"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT video_timestamp
                FROM youtube.youtube_subtitles_summary
                WHERE author = :author
                ORDER BY video_timestamp DESC
                LIMIT 1
            """)
            result = conn.execute(query, {'author': author}).fetchone()
            if result:
                return result[0]
        return None
    except Exception as e:
        print(f"Error retrieving latest video timestamp: {e}")
        return None

def get_all_summaries() -> List[Dict]:
    """Retrieve all summaries from the database"""
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT video_id, title, video_content_summary, video_timestamp, author
                FROM youtube.youtube_subtitles_summary
            """)
            results = conn.execute(query).fetchall()
            return [{
                'video_id': row[0],
                'title': row[1],
                'video_content_summary': row[2],
                'video_timestamp': row[3],
                'author': row[4]
            } for row in results]
    except Exception as e:
        print(f"Error retrieving all summaries: {e}")
        return []

def delete_summary(video_id: str) -> bool:
    """Delete a summary by video_id"""
    try:
        with engine.connect() as conn:
            query = text("""
                DELETE FROM youtube.youtube_subtitles_summary
                WHERE video_id = :video_id
            """)
            conn.execute(query, {'video_id': video_id})
            conn.commit()
        return True
    except Exception as e:
        print(f"Error deleting summary: {e}")
        return False