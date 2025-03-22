import logging
from rich.logging import RichHandler
from rich.console import Console
try:
    import tweepy
except ImportError:
    raise ImportError("Run 'pip install tweepy' to install tweepy")

# Configure rich logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=False)]
)
logger = logging.getLogger("XTools")


class XTools:
    """X Tool to interact with X"""
    def __init__(self, consumer_key: str, consumer_secret: str, 
                 access_token: str, access_token_secret: str):
        """Initialize XTools with X API credentials.
        
        Args:
            consumer_key: X API consumer key
            consumer_secret: X API consumer secret
            access_token: X API access token
            access_token_secret: X API access token secret
        """
        logger.info('Initializing XTools with API credentials')
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        logger.info('Tweepy client initialized successfully')

    def create_tweet(self, text: str) -> str:
        """Create a new tweet with the given text.
        
        Args:
            text: The content of the tweet
            
        Returns:
            String representation of response containing tweet ID
        """
        logger.info(f'Creating tweet: {text}...')
        try:
            response = self.client.create_tweet(text=text)
            tweet_id = response.data.get('id', '')
            logger.info(f'Tweet created successfully with ID: {tweet_id}')
            return str({'id': tweet_id})
        except Exception as e:
            logger.error(f'Failed to create tweet: {str(e)}')
            return str(e)

    def delete_tweet(self, id: str) -> str:
        """Delete a tweet with the specified ID.
        
        Args:
            id: The ID of the tweet to delete
            
        Returns:
            String representation of the API response or error message
        """
        logger.info(f'Attempting to delete tweet with ID: {id}')
        try:
            response = self.client.delete_tweet(id=id)
            logger.info(f'Tweet {id} deleted successfully')
            return str(response.data)
        except Exception as e:
            logger.error(f'Failed to delete tweet {id}: {str(e)}')
            return str(e)

    def like_tweet(self, tweet_id: str) -> str:
        """Like a tweet by its ID.
        
        Args:
            tweet_id: The ID of the tweet to like
            
        Returns:
            String representation of the like status
        """
        logger.info(f'Liking tweet with ID: {tweet_id}')
        try:
            response = self.client.like(tweet_id=tweet_id)
            status = response.data.get('liked', False)
            logger.info(f'Tweet {tweet_id} like status: {status}')
            return str({'liked': status})
        except Exception as e:
            logger.error(f'Failed to like tweet {tweet_id}: {str(e)}')
            return str(e)

    def unlike_tweet(self, tweet_id: str) -> str:
        """Unlike a tweet by its ID.
        
        Args:
            tweet_id: The ID of the tweet to unlike
            
        Returns:
            String representation of the like status
        """
        logger.info(f'Unliking tweet with ID: {tweet_id}')
        try:
            response = self.client.unlike(tweet_id=tweet_id)
            status = response.data.get('liked', False)
            logger.info(f'Tweet {tweet_id} unlike completed')
            return str({'liked': status})
        except Exception as e:
            logger.error(f'Failed to unlike tweet {tweet_id}: {str(e)}')
            return str(e)

    def retweet(self, tweet_id: str) -> str:
        """Retweet a tweet by its ID.
        
        Args:
            tweet_id: The ID of the tweet to retweet
            
        Returns:
            String representation of the retweet status
        """
        logger.info(f'Retweeting tweet with ID: {tweet_id}')
        try:
            response = self.client.retweet(tweet_id=tweet_id)
            status = response.data.get('retweeted', False)
            logger.info(f'Tweet {tweet_id} retweet status: {status}')
            return str({'retweeted': status})
        except Exception as e:
            logger.error(f'Failed to retweet {tweet_id}: {str(e)}')
            return str(e)

    def unretweet(self, tweet_id: str) -> str:
        """Unretweet a tweet by its ID.
        
        Args:
            tweet_id: The ID of the tweet to unretweet
            
        Returns:
            String representation of the retweet status
        """
        logger.info(f'Unretweeting tweet with ID: {tweet_id}')
        try:
            response = self.client.unretweet(tweet_id=tweet_id)
            status = response.data.get('retweeted', False)
            logger.info(f'Tweet {tweet_id} unretweet completed')
            return str({'retweeted': status})
        except Exception as e:
            logger.error(f'Failed to unretweet {tweet_id}: {str(e)}')
            return str(e)

    def get_user_timeline(self, user_id: str, max_results: int = 10) -> str:
        """Fetch recent tweets from a user's timeline.
        
        Args:
            user_id: The ID of the user whose timeline to fetch
            max_results: Maximum number of tweets to return (default: 10)
            
        Returns:
            String representation of the list of tweets
        """
        logger.info(f'Fetching timeline for user ID: {user_id} (max: {max_results} tweets)')
        try:
            tweets = self.client.get_users_tweets(id=user_id, max_results=max_results)
            tweet_list = [tweet.text for tweet in tweets.data] if tweets.data else []
            logger.info(f'Retrieved {len(tweet_list)} tweets from user {user_id}')
            return str(tweet_list)
        except Exception as e:
            logger.error(f'Failed to fetch timeline for user {user_id}: {str(e)}')
            return str(e)

    def search_tweets(self, query: str, max_results: int = 10) -> str:
        """Search recent tweets by keyword or query.
        
        Args:
            query: Search query (e.g., 'python -is:retweet')
            max_results: Maximum number of tweets to return (default: 10)
            
        Returns:
            String representation of the list of matching tweets
        """
        logger.info(f'Searching tweets with query: {query} (max: {max_results} tweets)')
        try:
            tweets = self.client.search_recent_tweets(query=query, max_results=max_results)
            tweet_list = [tweet.text for tweet in tweets.data] if tweets.data else []
            logger.info(f'Retrieved {len(tweet_list)} tweets for query: {query}')
            return str(tweet_list)
        except Exception as e:
            logger.error(f'Failed to search tweets with query {query}: {str(e)}')
            return str(e)

    def follow_user(self, target_user_id: str) -> str:
        """Follow a user by their ID.
        
        Args:
            target_user_id: The ID of the user to follow
            
        Returns:
            String representation of the follow status
        """
        logger.info(f'Following user with ID: {target_user_id}')
        try:
            response = self.client.follow_user(target_user_id=target_user_id)
            status = response.data.get('following', False)
            logger.info(f'Follow status for user {target_user_id}: {status}')
            return str({'following': status})
        except Exception as e:
            logger.error(f'Failed to follow user {target_user_id}: {str(e)}')
            return str(e)

    def unfollow_user(self, target_user_id: str) -> str:
        """Unfollow a user by their ID.
        
        Args:
            target_user_id: The ID of the user to unfollow
            
        Returns:
            String representation of the follow status
        """
        logger.info(f'Unfollowing user with ID: {target_user_id}')
        try:
            response = self.client.unfollow_user(target_user_id=target_user_id)
            status = response.data.get('following', False)
            logger.info(f'Unfollow status for user {target_user_id}: {status}')
            return str({'following': status})
        except Exception as e:
            logger.error(f'Failed to unfollow user {target_user_id}: {str(e)}')
            return str(e)

    def get_user_details(self, username: str) -> str:
        """Get user details by their username.
        
        Args:
            username: The username of the user to lookup
            
        Returns:
            String representation of the user details
        """
        logger.info(f'Fetching details for user: {username}')
        try:
            user = self.client.get_user(username=username)
            user_info = {'id': user.data.id, 'name': user.data.name, 'username': user.data.username} if user.data else {}
            logger.info(f'Retrieved details for user: {username}')
            return str(user_info)
        except Exception as e:
            logger.error(f'Failed to fetch details for user {username}: {str(e)}')
            return str(e)
        
    def get_followers(self, user_id: str, max_results: int = 10) -> str:
        """Get a list of followers for a user by their ID.
        
        Args:
            user_id: The ID of the user whose followers to fetch
            max_results: Maximum number of followers to return (default: 10)
            
        Returns:
            String representation of the list of followers
        """
        logger.info(f'Fetching followers for user ID: {user_id} (max: {max_results} followers)')
        try:
            followers = self.client.get_users_followers(id=user_id, max_results=max_results)
            follower_list = [follower.username for follower in followers.data] if followers.data else []
            logger.info(f'Retrieved {len(follower_list)} followers for user {user_id}')
            return str(follower_list)
        except Exception as e:
            logger.error(f'Failed to fetch followers for user {user_id}: {str(e)}')
            return str(e)