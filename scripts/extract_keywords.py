import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
nltk.download('stopwords')
stopwords = set(nltk.corpus.stopwords.words('english'))

def keyword_extraction():
    df = pd.read_csv('data/cleaned_data.csv')
    texts = df['title'].fillna('') + ' ' + df['description'].fillna('')
    vectorizer = TfidfVectorizer(stop_words=stopwords, max_features=20)
    vectorizer.fit(texts)
    keywords = vectorizer.get_feature_names_out()
    df['top_keyword'] = vectorizer.transform(texts).toarray().argmax(axis=1)
    df['top_keyword'] = [keywords[idx] if 0 <= idx < len(keywords) else '' for idx in df['top_keyword']]
    df.to_csv('data/cleaned_data.csv', index=False)

if __name__ == "__main__":
    keyword_extraction()
