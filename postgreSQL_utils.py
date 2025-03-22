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

def save_summary(video_id: str, title: str, video_content_summary: str, video_timestamp: str, author: str) -> bool:
    """Save a new summary record to the database"""
    print("Saving summary...")
    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO youtube.youtube_subtitles_summary 
                (video_id, title, video_content_summary, video_timestamp, author)
                VALUES (:video_id, :title, :video_content_summary, :video_timestamp, :author)
                ON CONFLICT (video_id) DO UPDATE SET
                title = EXCLUDED.title,
                video_content_summary = EXCLUDED.video_content_summary,
                video_timestamp = EXCLUDED.video_timestamp,
                author = EXCLUDED.author
            """)
            conn.execute(query, {
                'video_id': video_id,
                'title': title,
                'video_content_summary': video_content_summary,
                'video_timestamp': video_timestamp,
                'author': author
            })
            conn.commit()
        return True
    except Exception as e:
        print(f"Error saving summary: {e}")
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