import requests
import os
from openai import AzureOpenAI
import flet as ft
import json

from dotenv import load_dotenv
load_dotenv()

from data.data_cleaning import clean_data

from newsapi import NewsApiClient


newsapi = NewsApiClient(
	api_key=os.getenv("NEWS_API_KEY")                   
)

def fetch_news_data():
    return newsapi.get_top_headlines(
    	category='business', 
    	language='en',
    	country='us',
        page_size=5
	)
  
model_name = os.getenv("MODEL_NAME")

client = AzureOpenAI(
	azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),
    api_version = os.getenv("API_VERSION"),
)

def summarize_with_openai():
    processed_articles = clean_data(fetch_news_data())
        
    prompt = f"""
    You are a professional stock market analyst. Here are the latest news articles:

    {processed_articles}

    For each article:
    1. Summarize it in 2-3 sentences.
    2. Rank it on a scale of 1-5 for usefulness in predicting stock market trends.
    3. Provide a short rationale for the ranking.
    4. Based on the market trends, recommend which stocks to purchase.

    Format your output as a JSON array of objects, with keys: title, summary, usefulness, reason, recommendedStocks (as a list of stock symbols), date published.
    Respond ONLY with the JSON array, no extra text.
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a professional stock market analyst. Your job is to rank news articles by how useful they are for predicting market trends. Provide clear reasoning."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_completion_tokens=3000
    )
    text_output = response.choices[0].message.content.strip()
    print("LLM raw output:\n", text_output)  # Debug: print raw output

    if not text_output:
        print("Warning: LLM returned empty output.")
        return []

    try:
        if not text_output.startswith("["):
            json_start = text_output.find("[")
            json_end = text_output.rfind("]") + 1
            text_output = text_output[json_start:json_end]
        articles = json.loads(text_output)
        return articles
    except Exception as e:
        print("Error parsing JSON from LLM output:", e)
        print("Raw output was:\n", text_output)
        return []

def refresh_news(page: ft.Page, container: ft.Column):
    ranked_articles = summarize_with_openai()

    container.controls.clear()
    for art in ranked_articles:
        card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(art.get("title", "N/A"), weight="bold", size=16),
                        ft.Text(f"Summary: {art.get('summary', 'N/A')}"),
                        ft.Text(f"Usefulness: {art.get('usefulness', 'N/A')}"),
                        ft.Text(f"Reason: {art.get('reason', 'N/A')}"),
                        ft.Text(
                            f"Recommendation: {', '.join(art.get('recommendedStocks', [])) if art.get('recommendedStocks') else 'N/A'}",
                            italic=True
                        )
                    ],
                    spacing=4,
                ),
                padding=10,
            ),
            elevation=3,
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

if __name__ == "__main__":
    ft.app(target=main)