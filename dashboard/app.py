import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from wordcloud import WordCloud
import joblib

st.set_page_config(page_title="YouTube Analytics", layout="wide")

# Load data
df = pd.read_csv('data/cleaned_data.csv')

# Preprocessing
df['engagement_rate'] = (df['likes'] + df['comments']) / df['views'].replace(0,1)
df['publishedAt'] = pd.to_datetime(df['publishedAt'])
df['upload_hour'] = df['publishedAt'].dt.hour
df['days_since_upload'] = (pd.Timestamp('now') - df['publishedAt']).dt.days.replace(0,1)
df['views_per_day'] = df['views'] / df['days_since_upload']

# SIDEBAR
st.sidebar.header("Filter & Visualization Options")

# Date filter
min_date, max_date = df['publishedAt'].min(), df['publishedAt'].max()
date_range = st.sidebar.date_input("Upload Date Range", 
                                   [min_date, max_date],
                                   min_value=min_date, max_value=max_date)
if isinstance(date_range, list) or isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

# Keyword filter
all_keywords = sorted(df['top_keyword'].dropna().unique())
selected_keywords = st.sidebar.multiselect("Filter by Keyword/Topic", all_keywords, default=[])

# Views/Likes/Engagement thresholds
min_views = st.sidebar.slider("Minimum Views", 0, int(df['views'].max()), 0)
min_likes = st.sidebar.slider("Minimum Likes", 0, int(df['likes'].max()), 0)
min_engagement = st.sidebar.slider("Minimum Engagement Rate (%)", 0, 100, 0)

# Video title search
search_term = st.sidebar.text_input("Search Video Title", "")

# Chart customization
trend_chart_type = st.sidebar.selectbox("Trend Chart Type", ["Line", "Scatter", "Bar"])

# Number of top entries
num_top = st.sidebar.slider("Show Top N Videos", 1, 50, 10)

# Apply user filters to DataFrame
filter_mask = (
    (df['publishedAt'] >= pd.to_datetime(start_date)) &
    (df['publishedAt'] <= pd.to_datetime(end_date)) &
    (df['views'] >= min_views) &
    (df['likes'] >= min_likes) &
    (df['engagement_rate']*100 >= min_engagement)
)
if selected_keywords:
    filter_mask &= df['top_keyword'].isin(selected_keywords)
if search_term:
    filter_mask &= df['title'].str.contains(search_term, case=False, na=False)

filtered_df = df[filter_mask]


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview", "Trends", "Sentiment", "Keywords/Topics", "Predictor"
])

with tab1:
    st.header("Channel Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Videos Analyzed", len(filtered_df))
    col2.metric("Total Views", int(filtered_df['views'].sum()))
    col3.metric("Median Engagement Rate", round(filtered_df['engagement_rate'].median()*100, 2))
    st.dataframe(filtered_df.sort_values('views', ascending=False)[['title','views','engagement_rate']].head(num_top))

with tab2:
    st.header("Trend Analysis")
    chart_data = filtered_df.sort_values("publishedAt")
    if trend_chart_type == "Line":
        fig = px.line(chart_data, x='publishedAt', y='views', title="Views Over Time")
    elif trend_chart_type == "Bar":
        fig = px.bar(chart_data, x='publishedAt', y='views', title="Views Over Time")
    else:
        fig = px.scatter(chart_data, x='duration_sec', y='views', color='engagement_rate', 
                         hover_data=['title'], title="Views vs Duration vs Engagement Rate")
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Trending Videos (Highest Views/Day)")
    st.dataframe(filtered_df.sort_values('views_per_day', ascending=False)[['title','views','views_per_day']].head(num_top))

with tab3:
    st.header("Audience Sentiment")
    fig, ax = plt.subplots()
    ax.hist(filtered_df['avg_sentiment'].dropna(), bins=20, color='salmon')
    ax.set_xlabel('Average Comment Sentiment')
    ax.set_ylabel('Count')
    st.pyplot(fig)
    st.write("Most Positive Videos")
    st.dataframe(filtered_df.sort_values('avg_sentiment', ascending=False)[['title','avg_sentiment']].head(5))

with tab4:
    st.header("Top Keywords/Topics & Word Cloud")
    keywords = filtered_df['top_keyword'].value_counts().head(10)
    st.bar_chart(keywords)
    st.subheader("Word Cloud of Video Titles & Descriptions (Filtered)")
    text = ' '.join(filtered_df['title'].astype(str)) + ' ' + ' '.join(filtered_df['description'].astype(str))
    if text.strip():
        wc = WordCloud(width=800, height=400, background_color='white').generate(text)
        fig2, ax2 = plt.subplots(figsize=(8,4))
        ax2.imshow(wc, interpolation='bilinear')
        ax2.axis('off')
        st.pyplot(fig2)
    else:
        st.write("No text to display word cloud (your filters may be too strict).")

with tab5:
    st.header("Predict Future View Counts")
    st.write("Estimate expected views using duration, likes, comments, and sentiment.")
    duration = st.number_input("Duration (seconds)", 0, int(df['duration_sec'].max()), 300)
    likes = st.number_input("Likes", 0, int(df['likes'].max()), 100)
    comments = st.number_input("Comments", 0, int(df['comments'].max()), 10)
    sentiment = st.slider("Avg. Sentiment", -1.0, 1.0, 0.0, 0.01)
    model = joblib.load('output/youtube_views_predictor.joblib')
    predicted_views = model.predict([[duration, likes, comments, sentiment]])
    st.success(f"Predicted Views: {int(predicted_views[0]):,.0f}")

