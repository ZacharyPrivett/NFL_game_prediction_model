import requests
import os
from openai import AzureOpenAI

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import AzureChatOpenAI

client = AzureOpenAI(
	azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    api_version = os.getenv("API_VERSION"),
    news_api_key = os.getenv("NEWS_API_KEY")
)
