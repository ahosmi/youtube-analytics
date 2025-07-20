import json
from googleapiclient.discovery import build
from config import get_api_key

def get_youtube_client():
    api_key = get_api_key()
    return build('youtube', 'v3', developerKey=api_key)

def fetch_comments(video_id, max_comments=50):
    youtube = get_youtube_client()
    comments = []
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=min(max_comments, 100)
    ).execute()
    for item in response.get('items', []):
        text = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(text)
    return comments

def fetch_comments_bulk():
    with open('data/raw_videos.json', 'r', encoding='utf-8') as f:
        video_data = json.load(f)
    comments_data = {}
    for video in video_data:
        vid = video['id']
        comments_data[vid] = fetch_comments(vid, max_comments=50)
    with open('data/video_comments.json', 'w', encoding='utf-8') as f:
        json.dump(comments_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    fetch_comments_bulk()
