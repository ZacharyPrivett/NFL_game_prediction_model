def clean_data(top_headlines):
    cleaned_articles = []
    for article in top_headlines['articles']:
        cleaned = {
            "source": article.get("source", {}).get("name"),
            "author": article.get("author"),
            "title": article.get("title"),
            "description": article.get("description"),
            "url": article.get("url"),
            "publishedAt": article.get("publishedAt")
        }
        cleaned_articles.append(cleaned)
        for article in cleaned_articles:
            print(article)
    return cleaned_articles