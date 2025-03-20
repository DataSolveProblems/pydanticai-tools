import logging
from typing import List, Optional
from pydantic import BaseModel, Field
try:
    from googlesearch import search
except ImportError:
    raise ImportError("`googlesearch-python` not installed. Please install using `pip install googlesearch-python`")

from rich.logging import RichHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)
logger = logging.getLogger("GoogleSearchTools")

# try:
#     from pycountry import pycountry
# except ImportError:
#     raise ImportError("`pycountry` not installed. Please install using `pip install pycountry`")

class GoogleSearchResult(BaseModel):
    url: str = Field(..., description="URL of the search result")
    title: Optional[str] = Field(None, description="Title of the search result")
    description: Optional[str] = Field(None, description="Description of the search result")
    
class GoogleSearchResults(BaseModel):
    result_count: int = Field(..., description="Number of search results")
    results: List[GoogleSearchResult] = Field(..., description="List of search results")


class GoogleSearchTool:
    """
    GoogleSearch is a Python library for searching Google easily.
    It uses requests and BeautifulSoup4 to scrape Google.

    Args:
        default_language (Optional[str]): Default language for search results, default is 'en' (English).
        timeout (Optional[int]): Timeout for the request, default is 10 seconds.
    """

    def __init__(
        self,
        default_language: Optional[str] = 'en',
        timeout: Optional[int] = 10,
    ):
        self.default_language = default_language
        self.timeout = timeout

    def google_search(
            self, 
            query: str, 
            max_results: int = 5, 
            start_number: int = 0, 
            language: str = "en", 
            advanced: bool = False
        ) -> str:
        """
        Use this function to search Google for a specified query.

        Args:
            query (str): The search query.
            max_results (int): The maximum number of results to return. Default is 5.
            start_number (int): The starting index for the search results. Default is 0.
            language (str): The language for the search results. Default is 'en'.
            advanced (bool): Whether to use advanced search options. Default is False.

        Returns:
            GoogleSearchResults: A list of search results.
        """
        logger.info(f"Searching Google for: {query}")

        # Perform Google search using the googlesearch-python package
        results = search(
            term=query, 
            num_results=max_results, 
            lang=language, 
            advanced=advanced,
            start_num=start_number,
        )

        # Collect the search results
        search_results = []
        for result in results:
            if advanced:
                search_results.append(
                    GoogleSearchResult(
                        url=result.url,
                        title=result.title,
                        description=result.description,
                    )
                )
            else:
                search_results.append(
                    GoogleSearchResult(
                        url=result,
                        title=None,
                        description=None,
                    )
                )

        logger.info(f"Found {len(search_results)} results")

        # Create a GoogleSearchResults object
        google_search_results = GoogleSearchResults(
            result_count=len(search_results),
            results=search_results
        )
        
        return google_search_results

if __name__ == '__main__':
    # # Example usage
    # google_search_tool = GoogleSearchTools()
    # query = "OpenAI GPT-3"
    # results = google_search_tool.google_search(query)
    # print(results)
    search_tool = GoogleSearchTool()

    query = '1784 NW Northrup St, Portland, OR 97209'

    response = search_tool.google_search(
        query=query,
        max_results=5,
        start_number=0,
        language='en',
        advanced=True
    )

    for result in response.results:
        print(result.url)
        print(result.title)
        print(result.description)
        print()
