from bs4 import BeautifulSoup
import httpx

def get_page_content(url: str, headers: dict = None) -> str:
    """
    Fetch the content of a web page using HTTP GET request.
    
    Args:
        url: The URL of the page to fetch
        
    Returns:
        The content of the page as a string, or an empty string if an error occurs
    """
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

    try:
        response = httpx.get(
            url, 
            headers=headers, 
            timeout=10.0,
            follow_redirects=True
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.text.replace('\n', ' ')
    except httpx.HTTPStatusError as e:
        print(f"Error fetching page content: HTTP {e.response.status_code}. {e.response.text}")
        return ''
    except httpx.RequestError as e:
        print(f"Request error: {str(e)}")
        return ''
    except Exception as e:
        print(f"Unexpected error fetching page content: {str(e)}")
        return ''
    
if __name__ == '__main__':
    url = 'https://ai.google.dev/gemini-api/docs/prompting-strategies'
    content = get_page_content(url)
