import json
import pandas as pd
import isodate

def parse_duration(duration):
    try:
        return int(isodate.parse_duration(duration).total_seconds())
    except Exception:
        return None

def clean_json_to_csv():
    with open('data/raw_videos.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    records = []
    for item in data:
        stats = item.get('statistics', {})
        snippet = item.get('snippet', {})
        duration = item.get('contentDetails', {}).get('duration', '')
        record = {
            'video_id': item['id'],
            'title': snippet.get('title', ''),
            'description': snippet.get('description', ''),
            'publishedAt': snippet.get('publishedAt', ''),
            'views': int(stats.get('viewCount', 0)),
            'likes': int(stats.get('likeCount', 0) or 0),
            'comments': int(stats.get('commentCount', 0) or 0),
            'duration_sec': parse_duration(duration)
        }
        records.append(record)
    df = pd.DataFrame(records)
    df.to_csv('data/cleaned_data.csv', index=False)

if __name__ == "__main__":
    clean_json_to_csv()
