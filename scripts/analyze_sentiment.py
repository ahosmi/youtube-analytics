import json
import pandas as pd
from textblob import TextBlob

def analyze_comment_sentiment(comment):
    try:
        return TextBlob(comment).sentiment.polarity
    except:
        return 0

def compute_video_sentiments():
    with open('data/video_comments.json', 'r', encoding='utf-8') as f:
        comments_data = json.load(f)
    sentiments = {}
    for vid, comments in comments_data.items():
        scores = [analyze_comment_sentiment(comm) for comm in comments]
        avg = sum(scores)/len(scores) if scores else 0
        sentiments[vid] = avg
    df_sentiment = pd.DataFrame(sentiments.items(), columns=['video_id','avg_sentiment'])
    video_df = pd.read_csv('data/cleaned_data.csv')
    merged = video_df.merge(df_sentiment, on='video_id', how='left')
    merged.to_csv('data/cleaned_data.csv', index=False)  

if __name__ == "__main__":
    compute_video_sentiments()
