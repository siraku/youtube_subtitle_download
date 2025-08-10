from google import genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
API_KEY = os.getenv('YOUTUBE_API_KEY')
client = genai.Client(api_key=API_KEY)

# Generate content
def generate_content(subtitles):
    print("Gemini Generating content...")
    response = client.models.generate_content(
    model="gemini-2.5-flash", contents="请帮忙总结下面的youtube字幕，要求用要点方式。不重要的信息可以忽略掉"+subtitles)
    
    return response.text
    
    # "please summarize this youtube vides subtitles in bullet points.the output language corresponds to the subtitles. subtitles:"
