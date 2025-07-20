import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def train_and_save_model():
    df = pd.read_csv('data/cleaned_data.csv')
    features = df[['duration_sec', 'likes', 'comments', 'avg_sentiment']].fillna(0)
    target = df['views']
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    import joblib
    joblib.dump(model, 'output/youtube_views_predictor.joblib')

if __name__ == "__main__":
    train_and_save_model()
