import asyncio
import httpx
from pydantic import BaseModel, Field
from typing import List

class WebResult(BaseModel):
    title: str = Field(..., description='Title of the web result')
    url: str = Field(..., description='URL of the web result')
    is_source_local: bool = Field(..., description='Whether the source is local')
    description: str = Field(..., description='Description of the web result')
    page_age: str = Field(..., description='A date representing the age of the web page (when the page was created or published)')
    sub_type: str = Field(..., description='Subtype of the web result')
    age: str = Field(..., description='A string representing the age of the web search result (when the content was indexed or became available in search results)')

class WebResults(BaseModel):
    results: List[WebResult] = Field(..., description='List of web search results')    

class BraveSearchTool:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = 'https://api.search.brave.com/res/v1/web/search'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    async def web_search(
        self,
        q: str,
        country: str = 'US',
        search_lang: str = 'en',
        ui_lang: str = 'en-US',
        count: int = 20,
        offset: int = 0,
        safesearch: str = 'moderate',
        freshness: str = None,
        spellcheck: bool = True,
        result_filter: str = None,
        units: str = 'metric',
        extra_snippets: bool = False,
        total_results: int = 20,
    ) -> WebResults:
        """Perform a web search using the Brave Search API.
        
        Args:
            q: The user's search query term. Query cannot be empty. Maximum of 400 
                characters and 50 words.
            country: The search query country, where the results come from.
                Limited to 2 character country codes of supported countries.
                Defaults to "US".
            search_lang: The search language preference.
                The 2 or more character language code for search results.
                Defaults to "en".
            ui_lang: User interface language preferred in response.
                Usually of the format '<language_code>-<country_code>'.
                Defaults to "en-US".
            count: The number of search results returned in response.
                The maximum is 20. The actual number delivered may be less than 
                requested. Defaults to 20.
            offset: Zero-based offset for pagination. The maximum is 9.
                Use with count to paginate results. Defaults to 0.
            safesearch: Filters search results for adult content.
                Values: "off", "moderate", "strict". Defaults to "moderate".
            freshness: Filters search results by when they were discovered.
                Values: "pd" (24h), "pw" (7d), "pm" (31d), "py" (365d), 
                or date range "YYYY-MM-DDtoYYYY-MM-DD". Defaults to None.
            spellcheck: Whether to spellcheck provided query. Defaults to True.
            result_filter: Comma delimited string of result types to include.
                Values: "discussions", "faq", "infobox", "news", "query", 
                "summarizer", "videos", "web", "locations". Defaults to None.
            units: The measurement units. Values: "metric", "imperial".
                If not provided, units are derived from search country.
                Defaults to 'metric'.
            extra_snippets: Allow up to 5 additional, alternative excerpts.
                Only available under specific plans. Defaults to False.
            total_results: Maximum number of total results to return. May require
                multiple API calls as the API limits to 20 results per request.
                Defaults to 20.
        
        Returns:
            WebResults: The search results from the Brave Search API.
        """
        # Limit count to 20 (API maximum)
        api_count = min(count, 20)
        
        # Initialize with first batch of results
        all_results = []
        current_offset = offset
        remaining_results = total_results
        
        # Make multiple API calls if needed to reach total_results
        while remaining_results > 0:
            batch_count = min(api_count, remaining_results)
            
            params = {
                'q': q,
                'country': country,
                'search_lang': search_lang,
                'ui_lang': ui_lang,
                'count': batch_count,
                'offset': current_offset,
                'safesearch': safesearch,
                'spellcheck': int(spellcheck),
            }
            
            # Add optional parameters only if they are provided
            if freshness:
                params['freshness'] = freshness
            if result_filter:
                params['result_filter'] = result_filter
            if units:
                params['units'] = units
            if extra_snippets is not None:
                params['extra_snippets'] = int(extra_snippets)
                
            headers = self.headers.copy()
            headers['X-Subscription-Token'] = self.api_key
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params=params,
                    headers=headers
                )
                
                response.raise_for_status()
                batch_results = response.json()
            
            # Store the entire response for the first batch
            if current_offset == offset:
                combined_results = batch_results
            
            # Add web results to our collection
            if 'web' in batch_results and 'results' in batch_results['web']:
                batch_web_results = batch_results['web']['results']
                all_results.extend(batch_web_results)
                
                # Update tracking variables
                fetched_count = len(batch_web_results)
                remaining_results -= fetched_count
                current_offset += fetched_count
                
                # If we got fewer results than requested, there are no more results
                if fetched_count < batch_count:
                    break
            else:
                # No results in this batch, so we're done
                break
                
            # Break if we've reached the maximum offset the API supports (9)
            if current_offset >= 9:
                break
        
        # Update the combined results with all fetched results
        if 'web' in combined_results:
            combined_results['web']['results'] = all_results[:total_results]

        # Convert results to WebResult objects, handling missing fields
        web_results = []
        for result in combined_results['web']['results']:
            web_result = WebResult(
                title=result.get('title', ''),
                url=result.get('url', ''),
                is_source_local=result.get('is_source_local', False),
                description=result.get('description', ''),
                page_age=result.get('page_age', ''),
                sub_type=result.get('sub_type', 'generic'),
                age=result.get('age', '')
            )
            web_results.append(web_result)
        
        return WebResults(results=web_results)

if __name__ == "__main__":
    # Example usage
    API_KEY = ''

    brave_search = BraveSearchTool(api_key=API_KEY)

    res = asyncio.run(brave_search.web_search('Claude Desktop MCP Tool Example', total_results=30))
    print(res)



