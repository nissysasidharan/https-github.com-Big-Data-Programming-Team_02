# -*- coding: utf-8 -*-
"""Tweeter_sentiment_analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zZ74wwhewdbo3AhLpMSlTGfmv_DRVO6F
"""

import tweepy
import pandas as pd 
import numpy as np
import re

API_key = 'uY3t53pR6igMyhNF1BUZbYlBn'
API_Secert = 'uc6oBlwN9zHi7js4B5utMZ7VV4FmTRHIsINgTIHcdhGr1P5i1H'
Bearer_token = 'AAAAAAAAAAAAAAAAAAAAAAk0aAEAAAAAFhrXFJkWmCqw8sslEoiX5F6Yv%2Fk%3DqrztMnGtiAyRXplSQH4jjyAFD2nUpiBcWG1fHqqap3cBJWVbyF'
Access_token = '1501634192475627534-wKXPDIodmZWRUzV3mz3mAYPWb6Bwwn'
Access_token_secret = 'qUPowcO67nVHb4ibl6uuGaHp9xOTCMD1etIAEBF86hlo6'

dir(tweepy)

# Auth = tweepy.OAuthHandler(API_key,API_Secert)

# dir(Auth)

auth = tweepy.OAuthHandler(
   API_key, API_Secert
)

api = tweepy.API(auth)

list_tweet = []

for tweet in tweepy.Cursor(api.search, q= 'Oil').items(200):
  list_tweet.append(tweet)

list_tweet.text

for i in range(0,15):
  print(list_tweet[i].text)

tweets = []
for i in range(0,len(list_tweet)):
 
  tweets.append(list_tweet[i].text)

  data_api = pd.DataFrame({'text':tweets}, index = range(0,len(tweets)))

data_api

!pip install transformers

sentiment_pipeline = pipeline("sentiment-analysis", model = "")

import torch
from transformers import AutoModel, AutoTokenizer 

bertweet = AutoModel.from_pretrained("vinai/bertweet-large")

tokenizer = AutoTokenizer.from_pretrained("vinai/bertweet-large")

# INPUT TWEET IS ALREADY NORMALIZED!
line = "DHEC confirms HTTPURL via @USER :crying_face:"

input_ids = torch.tensor([tokenizer.encode(line)])

with torch.no_grad():
    features = bertweet(input_ids)  # Models outputs are now tuples

features.last_hidden_state.shape



"""#Add twitter Extract part above """

data = pd.read_csv( "/content/drive/MyDrive/Bigdat2/training.1600000.processed.noemoticon.csv",delimiter= ',',encoding='latin-1', header= None )

data.columns = ['sentiment', 'id', 'date','from','user','tweet']

data = data.drop(['id','date','from','user'] ,axis =1)

new_data_po = data[data['sentiment']==4].sample(500)
new_data_ne = data[data['sentiment']==0].sample(500)

combined_df = pd.concat([new_data_ne,new_data_po])

combined_df.to_csv('tweeets_1000.csv')

combined_df.sentiment.value_counts()

import nltk
nltk.download('stopwords')

#Tokenizer, # cleaning , 
import re
import string
import nltk
import spacy
nlp = spacy.load('en')
ps = nltk.PorterStemmer()
nltk.download('wordnet')
stopwords = nltk.corpus.stopwords.words('english')

def cmb_fun(text):
  for t in nlp(text):
    if t.like_url:
      pass
    else:
      text = "".join([t for t in text if t not in string.punctuation])
      toke = re.split("\W+", text)
      final = [word for word in toke if word not in stopwords]
      stem_text = [ps.stem(word) for word in final]

  
  
  return stem_text
  # no_punct = [word for word in text if ]

# pd.set_option('display.max_colwidth' , 1000)
# data1.head(5)

combined_df['text_clean'] = combined_df['tweet'].apply(lambda x: cmb_fun(x))

combined_df.head()

combined_df.text_clean

!pip install transformers

!python --version

import transformers
tokenizer = transformers.DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = transformers.DistilBertModel.from_pretrained('distilbert-base-uncased')

text_df = combined_df['text_clean']
target_df = combined_df['sentiment']
# target_df = pd.get_dummies(target_df)

tokenized_data = text_df.apply(lambda x : tokenizer.encode(x, max_length= 30))

pd.set_option('display.width', 100)
tokenized_data

from tensorflow.keras.preprocessing.sequence import pad_sequences

input_text = pad_sequences(tokenized_data, maxlen=30, padding="post")

# input_text

attention_mask = np.where(input_text != 0 ,1,0)
attention_mask.shape, input_text.shape

import torch 

input = torch.tensor(input_text)
atten = torch.tensor(attention_mask)

print(input.shape)
print(atten.shape)

op = model(input, attention_mask = atten)
op[0].shape

dt = op.last_hidden_state[:,0,:].detach().numpy()
target_df_1 = target_df.to_numpy()

from sklearn.model_selection import train_test_split
train_X, valid_X, train_y, valid_y = train_test_split(dt, target_df_1, test_size = 0.2, random_state=15)

train_X.shape

train_y.shape

from sklearn.ensemble import RandomForestClassifier

!pip install mlflow

"""##adding MLFlow"""

from pprint import pprint
import numpy as np
from sklearn.linear_model import LinearRegression
import mlflow

def fetch_logged_data(run_id):
    client = mlflow.tracking.MlflowClient()
    data = client.get_run(run_id).data
    tags = {k: v for k, v in data.tags.items() if not k.startswith("mlflow.")}
    artifacts = [f.path for f in client.list_artifacts(run_id, "model")]
    return data.params, data.metrics, tags, artifacts

train_y.shape

mlflow.sklearn.autolog()

clf = RandomForestClassifier(max_depth=2, random_state=0)
with mlflow.start_run() as run:
  clf.fit(train_X, train_y)

params, metrics, tags, artifacts = fetch_logged_data(run.info.run_id)

pprint(metrics)

# clf = RandomForestClassifier(max_depth=2, random_state=0)
# clf.fit(train_X, train_y)

from  sklearn.metrics  import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score
predictions = clf.predict(valid_X)
print(predictions)
predictions = np.round(predictions).astype(int)
print(predictions)
# print ("Accuracy :", np.round(accuracy_score(valid_y, predictions),5))
# print ("Precision :", np.round(precision_score(valid_y, predictions),5))
# print ("Recall :", np.round(recall_score(valid_y, predictions),5))
# print ("f1 score :", np.round(f1_score(valid_y, predictions),5))
# print ("AUC score :", np.round(roc_auc_score(valid_y, predictions),5))

import transformers
from tensorflow.keras.preprocessing.sequence import pad_sequences
import torch
import re
import string
import nltk
import spacy




def get_inputs(text:string):
  #Tokenizer, # cleaning , 

  nlp = spacy.load('en')
  ps = nltk.PorterStemmer()
  nltk.download('wordnet')
  stopwords = nltk.corpus.stopwords.words('english')
  
  for t in nlp(text):
    if t.like_url:
      pass
    else:
      text = "".join([t for t in text if t not in string.punctuation])
      toke = re.split("\W+", text)
      final = [word for word in toke if word not in stopwords]
      stem_text = [ps.stem(word) for word in final]

  tokenizer = transformers.DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
  model = transformers.DistilBertModel.from_pretrained('distilbert-base-uncased')
  tokenized = tokenizer.encode(stem_text)
  input_text = pad_sequences([tokenized], maxlen=30, padding="pre")
  attention_mask = np.where(input_text != 0 ,1,0)
  input = torch.tensor(input_text)
  atten = torch.tensor(attention_mask)
  op = model(input, attention_mask = atten)
  dt = op.last_hidden_state[:,0,:].detach().numpy()
  

  return dt

aa= get_inputs(' feeling like shit')

clf.predict(aa)