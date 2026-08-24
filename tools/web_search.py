#def web_search_SERP(state):
#     print(state["plan"])
#     print("Search Query:", state["plan"]["search_query"])

#     if state["plan"]["tool"] == "NA":
#         state["tool_result"] = "No search required"
#         print("-----------------------------------------------")
#         print(state["plan"]["tool"])
#         print("-----------------------------------------------")
#         return state
    
#     results = client.search({
#         "engine": "google",
#         "q": state["plan"]["search_query"],
#         "google_domain": "google.com",
#         "hl": "en",
#         "gl": "us"
#     })

#     state["tool_result"] = results["organic_results"]
#     print("Tool Result:", state["tool_result"])
#     return state
import asyncio
import json
import re

from config import llm_nvidia_hardcore, client   

from crawl4ai import (
    AsyncWebCrawler,
    CrawlerRunConfig,
    CacheMode
)


async def web_search_SERP(state: dict) -> dict:
    query = state.get("plan", {}).get("search_query", "")
    if not query:
        print("No search query in state")
        return state

    print(f"\nSearching Google for: {query}\n")

    def google_search(q: str):
        print(f"Performing Google search")
        try:
            results = client.search({
                "engine": "google",
                "q": q,
                "hl": "en",
                "gl": "us"
            })
            return [
                {
                    "title": r.get("title", ""),
                    "snippet": r.get("snippet", ""),
                    "url": r.get("link", "")
                }
                for r in results.get("organic_results", [])
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []

    search_results = google_search(query)


    def choose_urls(q: str, results):
        prompt = f"""..."""  

    print(f"Choosing URLs from search results")
    selected_urls = choose_urls(query, search_results)

    async def crawl_urls(urls):
        print(f"Crawling URLs")
        pass  

    crawled_pages = await crawl_urls(selected_urls)

    state.setdefault("search_results", {})
    state["search_results"].update({
        "query": query,
        "selected_urls": selected_urls[:3],
        "pages": crawled_pages
    })

    def answer_question(q: str, pages: list):
        if not pages:
            return "No content was crawled. Cannot generate answer."

        context = ""
        for page in pages:
            context += f"""
URL: {page.get('url', 'N/A')}

CONTENT:
{page.get('content', 'No content available')}

-----------------------------------------------------
"""

        prompt = f"""
You are an expert technical support assistant.

Answer the following question using ONLY the provided webpage content.
Be accurate, concise, and practical.

Question:
{q}

Webpages:
{context}

Provide a clear, structured response including:
- Direct answer
- Key explanations
- Step-by-step solutions if applicable
- Best practices or warnings
"""

        try:
            response = llm_nvidia_hardcore.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"Error generating final answer: {e}")
            return "Failed to generate final answer."

    final_answer = answer_question(query, crawled_pages)

    state["final_answer"] = final_answer
    state["search_results"]["final_answer"] = final_answer

    print("\nFinal answer generated and added to state.")
    return state


