import requests
import os
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

from data.data_cleaning import clean_data

from langchain_openai import AzureChatOpenAI

from newsapi import NewsApiClient

client = AzureOpenAI(
	azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("API_VERSION"),
    
)

newsapi = NewsApiClient(
	api_key=os.getenv("NEWS_API_KEY")                   
)

top_headlines = newsapi.get_top_headlines(
    category='business', 
    language='en',
    country='us'
)

articles = clean_data(top_headlines)
for article in articles:
    print(article)