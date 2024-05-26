from langchain_community.tools.tavily_search import TavilySearchResults
from .registry import action
from duckduckgo_search import DDGS
import json
import time

DUCKDUCKGO_MAX_ATTEMPTS = 3


@action(
    name="search",
    description="Search for information using Tavily",
    parameters=[
        {
            "name": "query",
            "description": "The search query to look up",
            "type": "str",
            "required": True
        }
    ],
    output_type="str"
)
def search(query: str) -> str:
    # Tavily search
    # tool = TavilySearchResults(max_results=5)
    # return tool.run(query)

    # DuckDuckGo search
    search_results = []
    attempts = 0
    num_results = 8

    while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
        if not query:
            return json.dumps(search_results)

        search_results = DDGS().text(query, max_results=num_results)

        if search_results:
            break

        time.sleep(1)
        attempts += 1

    results = json.dumps(search_results, ensure_ascii=False, indent=4)
    return safe_google_results(results)


def safe_google_results(results: str | list) -> str:
    """
        Return the results of a Google search in a safe format.

    Args:
        results (str | list): The search results.

    Returns:
        str: The results of the search.
    """
    if isinstance(results, list):
        safe_message = json.dumps(
            [result.encode("utf-8", "ignore").decode("utf-8") for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message
    

    
    




