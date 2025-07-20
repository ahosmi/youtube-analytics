import json
from googleapiclient.discovery import build
from config import get_api_key

def get_youtube_client():
    api_key = get_api_key()
    return build('youtube', 'v3', developerKey=api_key)

def search_videos_by_keyword(query, max_results=50):
    youtube = get_youtube_client()
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=min(max_results, 50)
    ).execute()
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    return video_ids

def get_video_stats(video_ids):
    youtube = get_youtube_client()
    video_stats = []
    for i in range(0, len(video_ids), 50):  # API batch limit
        batch_ids = ",".join(video_ids[i:i + 50])
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=batch_ids
        ).execute()
        video_stats.extend(response['items'])
    return video_stats

def fetch_and_save(query, max_results=50):
    video_ids = search_videos_by_keyword(query, max_results)
    video_data = get_video_stats(video_ids)
    with open('data/raw_videos.json', 'w', encoding='utf-8') as f:
        json.dump(video_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    fetch_and_save('YOUR_SEARCH_KEYWORD', max_results=100)
