"""News_Recommendation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1q56Mu-vjjSVnmDZ9BNcPac_SB8z83F3L
"""

import numpy as np
import pandas as pd

import math
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go


from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances

news=pd.read_json('news.json' , lines=True)

# news.info()

# news.head()

news=news[news['date']>=pd.Timestamp(2017,1,1)]

# news.shape

news=news[news['headline'].apply(lambda x: len(x.split())>5)]
# removing headlines with less than 5 words: headlines may become empty due to removal of stop words

news.drop_duplicates('headline' , inplace=True)

# news.isna().sum()

# news['category'].unique()

# news['category'].value_counts().sort_values(ascending=False)

news.index=range(news.shape[0])

# news['day and month']=news['date'].dt.strftime("%a")+news['date'].dt.strftime("%b")

news_temp=news.copy()

import nltk
nltk.download('stopwords')

stop_words=set(stopwords.words('english'))
# stop_words

def preprocess_headline(headline):
  headline=''.join(e for e in headline if e.isalnum() or e.isspace()).lower()
  words=[word for word in headline.split() if word not in stop_words]
  return ' '.join(words)

news_temp['headline']=news_temp['headline'].apply(preprocess_headline)

import nltk
nltk.download('punkt')

import nltk
nltk.download('wordnet')

lem=WordNetLemmatizer()
# Reduces words to their root form

for i in range(len(news_temp["headline"])):
    string = ""
    for w in word_tokenize(news_temp["headline"][i]):
        string += lem.lemmatize(w,pos = "v") + " "
    news_temp.at[i, "headline"] = string.strip()
    if(i%1000==0):
        print(i)

nltk.download('punkt')

nltk.download('wordnet')

# min_df=0

tfidf_headline_vectorizer=TfidfVectorizer()
tfidf_headline_features=tfidf_headline_vectorizer.fit_transform(news_temp['headline'])

tfidf_desc_vectorizer=TfidfVectorizer()
tfidf_desc_features=tfidf_desc_vectorizer.fit_transform(news_temp['short_description'])

tfidf_author_vectorizer=TfidfVectorizer()
tfidf_author_features=tfidf_author_vectorizer.fit_transform(news_temp['authors'])

from scipy.sparse import hstack

combined_features=hstack([
    tfidf_headline_features,
    tfidf_desc_features,
    tfidf_author_features,
    # tfidf_category_features
])

pd.set_option('display.max_colwidth' , None)

"""Preparing functions for recommending top 5 articles"""

import json

def preprocess_text(headline):
  headline=''.join(e for e in headline if e.isalnum() or e.isspace()).lower()
  words=[word for word in headline.split() if word not in stop_words]
  return ' '.join(words)

def vectorize_text(feature , vectorizer):
  tfidf_features=vectorizer.transform([feature])
  return tfidf_features

def combine_features(new_headline , new_description , new_author):
  headline_features = vectorize_text(new_headline ,tfidf_headline_vectorizer)
  description_features = vectorize_text(new_description ,tfidf_desc_vectorizer)
  author_features = vectorize_text(new_author ,tfidf_author_vectorizer)
  combined = hstack([headline_features, description_features, author_features])
  return combined

def recommend_similar_news(new_head , new_desc , new_author ,k):
  new_head=preprocess_text(new_head)
  new_desc=preprocess_text(new_desc)
  features_new_data=combine_features(new_head ,new_desc , new_author)
  couple_dist = pairwise_distances(combined_features,features_new_data)
  indices = np.argsort(couple_dist.ravel())[1:k+1]
  df = pd.DataFrame({'publish_date': news['date'][indices].dt.strftime('%Y-%m-%d').values,
               'headline':news['headline'][indices].values,
                'authors':news['authors'][indices].values,
                'desc':news['short_description'][indices].values,
                'category':news['category'][indices].values,
                'Euclidean similarity with the queried article': couple_dist[indices].ravel()})
  result_dict = df.to_dict(orient='records')

    # Convert dictionary to JSON
  result_json = json.dumps(result_dict, indent=4)

  return result_json

news.loc[12 ,'headline']

news.loc[12 ,'short_description']
demi = {"link":"https:\/\/www.huffpost.com\/entry\/covid-boosters-uptake-us_n_632d719ee4b087fae6feaac9","headline":"Over 4 Million Americans Roll Up Sleeves For Omicron-Targeted COVID Boosters","category":"U.S. NEWS","short_description":"Health experts said it is too early to predict whether demand would match up with the 171 million doses of the new boosters the U.S. ordered for the fall.","authors":"Carla K. Johnson, AP","date":1663891200000}
print(recommend_similar_news("Over 4 Million Americans Roll Up Sleeves For Omicron-Targeted COVID Boosters" ,"Health experts said it is too early to predict whether demand would match up with the 171 million doses of the new boosters the U.S. ordered for the fall.","Carla K. Johnson, AP",5))

