from postgreSQL_utils import save_summary

# Example usage
save_summary(
    video_id="abc123",
    title="Sample Video",
    video_content_summary="This is the summary text",
    video_timestamp=1234567890.0,
    author="John Doe"
)