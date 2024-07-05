from duckduckgo_search import DDGS
from main.bot.lib.tools import BaseTool
from pydantic import Field, validator
from typing import List, Optional
import requests
from bs4 import BeautifulSoup

class DuckSearch(BaseTool):
    """Use a SearchEngine to look up information on the internet."""
    query: str = Field(description="The query to search using DuckDuckGo.")
    k: int  = 5
    
    @validator('query')
    def query_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Query cannot be empty.")
        return v

    def run(self, query: str) -> str:
        """Use the tool."""
        return search_firstresult(query)

    async def async_run(self, query: str) -> str:
        """Use the tool asynchronously."""
        return search_firstresult(query)
    

def search(query: str) -> str:
    """Searches DuckDuckGo for a query."""
    ddgs = DDGS()
    return ddgs.text(query)[:5]

def search_firstresult(query: str) -> str:
    """Searches DuckDuckGo for a query and returns the first result."""
    ddgs = DDGS()
    msg = ""
    res = ddgs.text(query)
    # print(res)
   
    for i in range(4):
        msg += f"\nThis site {res[i]['title']} Contain the following information.\n {res[i]['body']}"
    

    return msg


def parse_and_get_webpage(query: str) -> str:
    """Parses the search results from DuckDuckGo."""
 
    results = search(query)
    content = ""
    for i in results:
        url = i["href"]
        webpage = requests.get(url) 
        bs = BeautifulSoup(webpage.content, 'html.parser')
        content += bs.get_text()


if __name__ == "__main__":
    print(search_firstresult("what is lycoris recoil"))