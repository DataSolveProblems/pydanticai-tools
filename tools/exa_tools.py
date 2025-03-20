import os
from typing import List, Optional, Literal, Union, Any
from pydantic import BaseModel, Field
# from exa_py.api import AnswerResponse, AnswerResult, Result

try:
    from exa_py import Exa
    # from exa_py.api import SearchResponse
except ImportError:
    raise ImportError("`exa_py` not installed. Please install using `pip install exa_py`")

class SearchResult(BaseModel):
    url: str = Field(..., title="URL of the search result")
    title: Optional[str] = Field(None, title="Title of the search result")
    score: Optional[float] = Field(None, title="Similarity score between query/url and result")
    published_date: Optional[str] = Field(None, title="Estimated creation date")
    author: Optional[str] = Field(None, title="Author of the content, if available")
    text: Optional[str] = Field(None, title="Full text of the search result")
    summary: Optional[str] = Field(None, title="Summary of the search result")

class SearchResults(BaseModel):
    cost_dollars: float = Field(..., title="Cost of the search in dollars")
    results: List[SearchResult] = Field(..., title="List of search results")


class ContentResult(BaseModel):
    url: str = Field(..., title="URL of the search result")
    title: Optional[str] = Field(None, title="Title of the search result")
    score: Optional[float] = Field(None, title="Similarity score between query/url and result")
    published_date: Optional[str] = Field(None, title="Estimated creation date")
    author: Optional[str] = Field(None, title="Author of the content, if available")
    text: Optional[str] = Field(None, title="Full text of the search result")
    summary: Optional[str] = Field(None, title="Summary of the search result")

class ContentResults(BaseModel):
    results: List[ContentResult] = Field(..., title="List of search results")

class AnswerResult_(BaseModel):
    """
    Represents a citation result from an Exa answer.
    """
    url: str = Field(..., title="URL of the search result")
    title: Optional[str] = Field(None, title="Title of the search result")
    published_date: Optional[str] = Field(None, title="Estimated creation date")
    author: Optional[str] = Field(None, title="Author of the content, if available")
    text: Optional[str] = Field(None, title="Full text of the search result")

class AnswerResults(BaseModel):
    answer: str = Field(..., title="The answer to the query")
    citations: List[AnswerResult_] = Field(..., title="List of citations")


class ExaTool:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("EXA_API_KEY")

        if not self.api_key:
            raise ValueError('EXA_API_KEY not set. Please set the EXA_API_KEY environment variable.')
        
        self.exa = Exa(api_key=self.api_key)

    def search(self, 
               query: str,
               num_results: Optional[int] = 10,
               include_domains: Optional[List[str]] = None,
               exclude_domains: Optional[List[str]] = None,
               start_crawl_date: Optional[str] = None,
               end_crawl_date: Optional[str] = None,
               start_published_date: Optional[str] = None,
               end_published_date: Optional[str] = None,
               use_autoprompt: Optional[bool] = False,
               type: Optional[str] = "auto",
               category: Optional[Literal[
                   'company', 'research paper', 'news', 'linkedin profile', 
                   'github', 'tweet', 'movie', 'song', 'personal site', 
                   'pdf', 'financial report'
               ]] = None
    ) -> SearchResults | str:
        """
        Perform an Exa search given an input query and retrieve a list of relevant results as links.

        Args:
            query: The input query string.
            num_results: Number of search results to return.
            include_domains: List of domains to include in the search.
            exclude_domains: List of domains to exclude in the search.
            start_crawl_date: Results will only include links crawled after this date.
            end_crawl_date: Results will only include links crawled before this date.
            start_published_date: Results will only include links published after this date.
            end_published_date: Results will only include links published before this date.
            use_autoprompt: If true, convert query to a query best suited for Exa.
            type: The type of search. Available types: keyword, neural, auto.
            category: A data category to focus on when searching. Available categories:
                     company, research paper, news, linkedin profile, github, tweet,
                     movie, song, personal site, pdf, and financial report.
        
        Returns:
            SearchResults object containing:
            - cost_dollars: Cost of the search in dollars
            - results: List of search results, each containing:
              - url (str): URL of the search result
              - title (Optional[str]): Title of the search result
              - score (Optional[float]): Similarity score between query/url and result
              - published_date (Optional[str]): Estimated creation date
              - author (Optional[str]): Author of the content, if available
        
            In case of error, returns error message as string.
        """
        try:
            response = self.exa.search(
                query=query,
                num_results=num_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                start_crawl_date=start_crawl_date,
                end_crawl_date=end_crawl_date,
                start_published_date=start_published_date,
                end_published_date=end_published_date,
                use_autoprompt=use_autoprompt,
                type=type,
                category=category
            )
            
            # Extract the cost
            cost_dollars = response.cost_dollars.total
            
            # Convert API results to our SearchResult objects
            search_results = []
            for result in response.results:
                search_result = SearchResult(
                    url=result.url,
                    title=result.title,
                    score=result.score,
                    published_date=result.published_date,
                    author=result.author,
                    text=result.text,
                    summary=result.summary
                )
                search_results.append(search_result)
            
            return SearchResults(cost_dollars=cost_dollars, results=search_results)
        except Exception as e:
            return f'Error: {str(e)}'
    
    def find_similar_results(
            self,
            url: str,
            num_results: Optional[int] = None,
            include_domains: Optional[List[str]] = None,
            exclude_domains: Optional[List[str]] = None,
            start_crawl_date: Optional[str] = None,
            end_crawl_date: Optional[str] = None,
            start_published_date: Optional[str] = None,
            end_published_date: Optional[str] = None,
            exclude_source_domain: Optional[bool] = None,
            category: Optional[Literal[
                'company', 'research paper', 'news', 'linkedin profile', 
                'github', 'tweet', 'movie', 'song', 'personal site', 
                'pdf', 'financial report'
            ]] = None
    ) -> SearchResults | str:
        """
        Find a list of similar results based on a webpage's URL.

        Args:
            url: The URL of the webpage to find similar results for.
            num_results: Number of similar results to return.
            include_domains: List of domains to include in the search.
            exclude_domains: List of domains to exclude from the search.
            start_crawl_date: Results will only include links crawled after this date.
            end_crawl_date: Results will only include links crawled before this date.
            start_published_date: Results will only include links with a published date after this date.
            end_published_date: Results will only include links with a published date before this date.
            exclude_source_domain: If true, excludes results from the same domain as the input URL.
            category: A data category to focus on when searching. Available categories:
                     company, research paper, news, linkedin profile, github, tweet,
                     movie, song, personal site, pdf, and financial report.
        
        Returns:
            SearchResults object containing:
            - cost_dollars: Cost of the search in dollars
            - results: List of search results, each containing:
              - url (str): URL of the search result
              - title (Optional[str]): Title of the search result
              - score (Optional[float]): Similarity score between query/url and result
              - published_date (Optional[str]): Estimated creation date
              - author (Optional[str]): Author of the content, if available
            
            In case of error, returns error message as string.
        """
        try:
            response = self.exa.find_similar(
                url=url,
                num_results=num_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                start_crawl_date=start_crawl_date,
                end_crawl_date=end_crawl_date,
                start_published_date=start_published_date,
                end_published_date=end_published_date,
                exclude_source_domain=exclude_source_domain,
                category=category
            )
            
            # Extract the cost
            cost_dollars = response.cost_dollars.total
            
            # Convert API results to our SearchResult objects
            search_results = []
            for result in response.results:
                search_result = SearchResult(
                    url=result.url,
                    title=getattr(result, 'title', None),
                    score=getattr(result, 'score', None),
                    published_date=getattr(result, 'published_date', None),
                    author=getattr(result, 'author', None),
                    text=getattr(result, 'text', None),
                    summary=getattr(result, 'summary', None)
                )
                search_results.append(search_result)
            
            return SearchResults(cost_dollars=cost_dollars, results=search_results)
        except Exception as e:
            return f'Error: {str(e)}'

    def get_answer(
        self,
        query: str,
        text: Optional[bool] = False,
    ) -> AnswerResults | str:
        """
        Generate an answer to a query using Exa's search and LLM capabilities.
        This method returns an AnswerResponse with the answer and a list of citations.
        You can optionally retrieve the full text of each citation by setting text=True.

        Args:
            query: The question to answer.
            text: If true, the full text of each citation is included in the result.
        
        Returns:
            AnswerResults object containing the answer and a list of citations.
            In case of error, returns error message as string.
        """
        try:
            response = self.exa.answer(
                query=query,
                text=text,
                stream=False
            )
            
            # Convert API citation results to our custom model
            citations = []
            for citation in response.citations:
                try:
                    citations.append(
                        AnswerResult_(
                            url=citation.url,
                            title=citation.title,
                            published_date=citation.published_date,
                            author=citation.author,
                            text=citation.text
                        )
                    )
                    
                except Exception as e:
                    print(f"Error converting citation: {str(e)}")
                    print(f"Citation data: {citation}")
                    # Continue with next citation if this one fails
                    continue
            
            # Create our custom AnswerResults model
            return AnswerResults(
                answer=response.answer,
                citations=citations
            )
        except Exception as e:
            return f'Error: {str(e)}'
        
    def get_contents(
        self,
        urls: List[str],
        full_page_text: Optional[bool] = False,
        summary: Optional[bool] = True,
        livecrawl: Optional[Literal['never', 'fallback', 'always', 'auto']] = None,
        livecrawl_timeout: Optional[int] = 10000,
    ) -> ContentResults | str:
        """
        Get the full page contents, summaries, and metadata for a list of URLs.
        Returns instant results from our cache, with automatic live crawling as fallback for uncached pages.

        Args:
            urls: Array of URLs to crawl (backwards compatible with 'ids' parameter).
            full_page_text: If true, Return full webpage text for every result, including for subpages
            summary: Summary of the webpage.
            livecrawl: Options for livecrawling pages:
                      'never': Disable livecrawling (default for neural search).
                      'fallback': Livecrawl when cache is empty (default for keyword search).
                      'always': Always livecrawl.
                      'auto': Use an LLM to detect if query needs real-time content.
            livecrawl_timeout: The timeout for livecrawling in milliseconds.

        Returns:
            ContentResults object containing the content information from the URLs.
            In case of error, returns error message as string.
        """
        try:
            api_results = self.exa.get_contents(
                urls=urls,
                text=full_page_text,
                summary=summary,
                livecrawl=livecrawl,
                livecrawl_timeout=livecrawl_timeout,
            ).results
            
            # Convert API results to our ContentResult objects
            content_results = []
            for result in api_results:
                content_result = ContentResult(
                    url=result.url,
                    title=getattr(result, 'title', None),
                    score=getattr(result, 'score', None),
                    published_date=getattr(result, 'published_date', None),
                    author=getattr(result, 'author', None),
                    text=getattr(result, 'text', None),
                    summary=getattr(result, 'summary', None)
                )
                content_results.append(content_result)
            
            return ContentResults(results=content_results)
        except Exception as e:
            return f'Error: {str(e)}'