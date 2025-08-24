import requests
import os
from openai import AzureOpenAI
import flet as ft
import json

from dotenv import load_dotenv
load_dotenv()

from data.data_cleaning import clean_data

from langchain_openai import AzureChatOpenAI

from newsapi import NewsApiClient


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
    
model_name = os.getenv("MODEL_NAME")

client = AzureOpenAI(
	azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    api_version = os.getenv("API_VERSION"),
)


### Zach - News data API call


### Justin - OpenAI call

def format_articles(articles):


def summarize_with_openai(articles):
	processed_articles = format_articles(articles)

	prompt = f"""
	You are a professional stock market analyst. Here are the latest news articles:

	{processed_articles}

	For each article:
	1. Summarize it in 2-3 sentences.
	2. Rank it on a scale of 1-5 for usefulness in predicting stock market trends.
	3. Provide a short rationale for the ranking.
	4. Based on the market trends. Recommend which stocks to purchase.

	Format your output clearly by article.

	"""

	response = client.chat.completions.create(
		model=model_name,
		messages=[
			{
				"role": "system",
				"content": "You are a professional stock market analyst, Your job is to rank news articles by how useful they are for predicting market trends. Provide clear reasoning"
			},
			{
				"role": "user",
				"content": prompt
			}
		],
		max_tokens=20
	)
	text_output = response.choices[0].message.content.strip()
    try:
        return json.loads(text_output)
    except json.JSONDecodeError:
        print("Error parsing JSON from LLM output")
        return []

def refresh_news(page: ft.Page, container: ft.Column):
    articles = fetch_headlines()
    ranked_articles = summarize_with_openai(articles)

    container.controls.clear()
    for art in ranked_articles:
        card = ft.Card(
            content=ft.Column(
                controls=[
                    ft.Text(art.get("title", "N/A"), weight="bold", size=16),
                    ft.Text(f"Summary: {art.get('summary', 'N/A')}"),
                    ft.Text(f"Usefulness: {art.get('usefulness', 'N/A')}"),
                    ft.Text(f"Reason: {art.get('reason', 'N/A')}", italic=True),
                ],
                spacing=4,
            ),
            elevation=3,
            padding=10,
        )
        container.controls.append(card)
    page.update()


def main(page: ft.Page):
    page.title = "Stock Market News Ranker"
    page.scroll = "auto"

    articles_container = ft.Column(spacing=10)

    refresh_button = ft.ElevatedButton(
        "Refresh News",
        on_click=lambda e: refresh_news(page, articles_container)
    )

    page.add(
        ft.Column(
            controls=[
                ft.Text("📰 AI Stock News Analyzer", size=22, weight="bold"),
                refresh_button,
                articles_container,
            ],
            spacing=20,
        )
    )

    refresh_news(page, articles_container)

