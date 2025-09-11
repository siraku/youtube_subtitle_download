import whisper

# Load the model (choose from tiny, base, small, medium, large)
model= whisper.load_model("base")
# model = whisper.load_model("base")  # "base" is a good balance of speed/accuracy
 
# Transcribe the MP3 file
result = model.transcribe("test.mp3")

# Save the transcription to a text file
with open("transcript.txt", "w", encoding="utf-8") as f:
    # Convert result to string if it's not already
    text_content = str(result["text"]) if isinstance(result["text"], list) else result["text"]
    f.write(text_content)
print("Transcription saved to transcript.txt")