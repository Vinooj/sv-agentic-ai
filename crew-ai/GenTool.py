import os
import json
from tavily import TavilyClient
from sklearn.metrics.pairwise import cosine_similarity

SEARCH_QUERY = "Latest Healthcare AI Related news"
MAX_ARTICLES = 25


CACHE_DIR = "files"
CACHE_FILEPATH = os.path.join(CACHE_DIR, "tavily_response.json")


def get_articles(query, max_results):
    """Fetches articles from Tavily API or loads from cache if it exists."""
    # Create cache directory if it doesn't exist
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    try:
        tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
        response = tavily.search(query=query, search_depth="basic", max_results=max_results)
        articles_data = response['results']
                
        # Save the fresh response to the cache file
        with open(CACHE_FILEPATH, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, indent=2)
            print(f"Saved new response to '{CACHE_FILEPATH}'.")
        return articles_data
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

print("Calling get_articles.")
articles = get_articles(SEARCH_QUERY, MAX_ARTICLES)
if not articles:
    print("No articles to process. Exiting.")
    exit()

print(f"Successfully loaded {len(articles)} articles.")