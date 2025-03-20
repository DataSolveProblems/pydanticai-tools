""" YouTube Tools based on Google YouTube Data API """
import json
from googleapiclient.discovery import Resource
from pydantic import BaseModel, Field
from .google_apis import create_service

# Data Models
class PlaylistInfo(BaseModel):
    playlist_id: str = Field(..., description='Playlist ID')
    playlist_title: str = Field(..., description='Playlist Title')
    channel_id: str = Field(..., description='Channel ID')
    description: str = Field(..., description='Playlist Description')
    # thumbnail_url: str = Field(..., description='Playlist Thumbnail')
    published_at: str = Field(..., description='Playlist Published Time')

class PlaylistResults(BaseModel):
    total_results: int = Field(..., description='Total number of results')
    playlists: list[PlaylistInfo] = Field(..., description='Playlist Information')

class ChannelInfo(BaseModel):
    channel_id: str = Field(..., description='Channel ID')
    channel_title: str = Field(..., description='Channel Title')
    description: str = Field(..., description='Channel Description')
    # thumbnail_url: str = Field(..., description='Channel Thumbnail')
    published_at: str = Field(..., description='Channel Published Time')
    country: str = Field(None, description='Channel Country')
    view_count: int = Field(None, description='View Count')
    subscriber_count: int = Field(None, description='Subscriber Count')
    video_count: int = Field(None, description='Video Count')

class ChannelResults(BaseModel):
    total_results: int = Field(..., description='Total number of results')
    channels: list[ChannelInfo] = Field(..., description='Channel Information')

class VideoInfo(BaseModel):
    channel_id: str = Field(..., description='Channel ID')
    channel_title: str = Field(..., description='Channel Title')
    video_id: str = Field(..., description='Video ID')
    video_title: str = Field(..., description='Video Title')
    description: str = Field(..., description='Video Description')
    # thumbnail_url: str = Field(..., description='Video Thumbnail')
    published_at: str = Field(..., description='Video Published Time')

    # Additional Information (optional)
    tags: list[str] = Field(None, description='Video Tags')
    duration: str = Field(None, description='Video Duration')
    dimension: str = Field(None, description='Video Dimension')
    view_count: int = Field(None, description='View Count')
    like_count: int = Field(None, description='Like Count')
    comment_count: int = Field(None, description='Comment Count')  # default to 0 to avoid type error
    topic_categories: list[str] = Field(None, description='Topic Categories')
    has_paid_product_placement: bool = Field(None, description='Has Paid Product Placement')

class VideoResults(BaseModel):
    total_results: int = Field(..., description='Total number of results')
    videos: list[VideoInfo] = Field(..., description='Video Information')


# YouTube Tool
class YouTubeTool:
    """  
    Toolkit for interacting with the YouTube Data API.

    Based on https://developers.google.com/youtube/v3/docs
    """
    API_NAME = 'youtube'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

    def __init__(self, client_secret: str) -> None:
        self.client_secret = client_secret
        self._init_youtube_service()

    def _init_youtube_service(self):
        """
        Initialize the YouTube Data API service.
        """
        self.service = create_service(
            self.client_secret,
            self.API_NAME,
            self.API_VERSION,
            self.SCOPES
        )
        print('service', self.service)

    # def __call__(self, *args, **kwargs):
    #     """
    #     Make the YouTubeTool instance callable.
    #     """
    #     # Implement the desired behavior when the instance is called
    #     # For example, you can call a default method or raise an error
    #     raise NotImplementedError("YouTubeTool instance is not directly callable. Use specific methods instead.")

    @property
    def youtube_service(self) -> Resource:
        """
        Return YouTube Data API service instance.
        """
        return self.service

    def get_channel_info(self, channel_id: str) -> ChannelInfo:
        """
        Get information about a YouTube channel based on the provided channel ID.

        Args:
            channel_id (str): The ID of the YouTube channel.
        
        Returns:
            ChannelInfo: Information about the YouTube channel.
        """
        request = self.service.channels().list(
            part='snippet,statistics',
            id=channel_id
        )
        response = request.execute()

        channel_info = ChannelInfo(
            channel_id=response['items'][0].get('id'),
            channel_title=response['items'][0]['snippet'].get('title'),
            description=response['items'][0]['snippet'].get('description'),
            # thumbnail_url=response['items'][0]['snippet']['thumbnails']['default']['url'],
            published_at=response['items'][0]['snippet'].get('publishedAt'),
            country=response['items'][0]['snippet'].get('country', ''),
            view_count=response['items'][0]['statistics'].get('viewCount'),
            subscriber_count=response['items'][0]['statistics'].get('subscriberCount'),
            video_count=response['items'][0]['statistics'].get('videoCount')  # use get to avoid KeyError
        )

        return channel_info.model_dump_json()

    
    def search_channel(self, channel_name: str,  published_after: str = None, published_before: str = None, region_code: str = 'US', order: str = 'relevance', max_results: int = 50) -> ChannelResults:
        """
        Searches for YouTube channels based on the provided channel name.
        
        Args:
            channel_name (str): The name of the channel to search for.
            published_after (str): The publishedAfter parameter indicates that the API response should only contain resources created at or after the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            published_before (str): The publishedBefore parameter indicates that the API response should only contain resources created before or at the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            region_code (str): The regionCode parameter instructs the API to return search results for the specified country. The parameter value is an ISO 3166-1 alpha-2 country code.
            order (str): The order in which to return results. Default is 'relevance'. Options include 'date', 'rating', 'relevance', 'title', 'videoCount', and 'viewCount'.
            max_results (int): The maximum number of results to return. Default is 50.

        Returns:
            ChannelResults: A list of channels that match the search
        """
        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            request = self.service.search().list(
                part='snippet',
                q=channel_name,
                type='channel',
                maxResults=min(50, max_results - len(lst)),
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                regionCode=region_code,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                channel_id = item['id'].get('channelId')
                channel_title = item['snippet'].get('title')
                channel_description = item['snippet'].get('description')
                # channel_thumbnail = item['snippet']['thumbnails']['default']['url']
                channel_published_at = item['snippet'].get('publishedAt')
                channel_info = ChannelInfo(
                    channel_id=channel_id,
                    channel_title=channel_title,
                    description=channel_description,
                    # thumbnail_url=channel_thumbnail,
                    published_at=channel_published_at
                )
                lst.append(channel_info)

            total_results = response['pageInfo']['totalResults']
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break
        
        return ChannelResults(
            total_results=total_results,
            channels=lst
        ).model_dump_json()

    def search_playlist(self, query: str, published_after: str = None, published_before: str = None, region_code: str = 'US', order: str = 'date', max_results: int = 50) -> PlaylistResults:
        """
        Searches for YouTube playlists based on the provided query.

        Args:
            query (str): The query to search for.
            published_after (str): The publishedAfter parameter indicates that the API response should only contain resources created at or after the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            published_before (str): The publishedBefore parameter indicates that the API response should only contain resources created before or at the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            region_code (str): The regionCode parameter instructs the API to return search results for the specified country. The parameter value is an ISO 3166-1 alpha-2 country code.
            order (str): The order in which to return results. Default is 'date'. Options include 'date', 'rating', 'relevance', 'title', 'videoCount', and 'viewCount'.
            max_results (int): The maximum number of results to return. Default is 50.

        Returns:
            PlaylistResults: A list of playlists that match the search
        """
        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            request = self.service.search().list(
                part='snippet',
                q=query,
                type='playlist',
                maxResults=min(50, max_results - len(lst)),
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                regionCode=region_code,                
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                playlist_id = item['id'].get('playlistId')
                playlist_title = item['snippet'].get('title')
                channel_id = item['snippet'].get('channelId')
                playlist_description = item['snippet'].get('description')
                # playlist_thumbnail = item['snippet']['thumbnails']['default']['url']
                playlist_published_at = item['snippet'].get('publishedAt')
                playlist_info = PlaylistInfo(
                    playlist_id=playlist_id,
                    playlist_title=playlist_title,
                    channel_id=channel_id,
                    description=playlist_description,
                    # thumbnail_url=playlist_thumbnail,
                    published_at=playlist_published_at
                )
                lst.append(playlist_info)

            total_results = response['pageInfo']['totalResults']
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return PlaylistResults(
            total_results=total_results,
            playlists=lst
        ).model_dump_json()

    def search_videos(self, query: str,  published_after: str = None, published_before: str = None, region_code: str = 'US', video_duration: str = 'any', order: str = 'date', max_results: int = 50) -> VideoResults:
        """
        Searches for YouTube videos based on the provided query.

        Args:
            query (str): The query to search for.
            published_after (str): The publishedAfter parameter indicates that the API response should only contain resources created at or after the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            published_before (str): The publishedBefore parameter indicates that the API response should only contain resources created before or at the specified time. The value is an RFC 3339 formatted date-time value (1970-01-01T00:00:00Z).
            region_code (str): The regionCode parameter instructs the API to return search results for the specified country. The parameter value is an ISO 3166-1 alpha-2 country code.
            video_duration (str): The videoDuration parameter filters video search results based on their duration. Default is 'Any'. Options include 'any', 'long', 'medium', 'short'.
            order (str): The order in which to return results. Default is 'date'. Options include 'date', 'rating', 'relevance', 'title', 'videoCount', and 'viewCount'.
            max_results (int): The maximum number of results to return. Default is 50.

        Returns:
            VideoResults: A list of videos that match the search
        """
        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            request = self.service.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=min(50, max_results - len(lst)),
                order=order,
                publishedAfter=published_after,
                publishedBefore=published_before,
                regionCode=region_code,
                videoDuration=video_duration,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                channel_id = item['snippet'].get('channelId')
                channel_title = item['snippet'].get('channelTitle')
                video_id = item['id'].get('videoId')
                video_title = item['snippet'].get('title')
                video_description = item['snippet'].get('description')
                # video_thumbnail = item['snippet']['thumbnails']['default']['url']
                video_published = item['snippet'].get('publishTime')
                video_info = VideoInfo(
                    channel_id=channel_id,
                    channel_title=channel_title,
                    video_id=video_id,
                    video_title=video_title,
                    description=video_description,
                    # thumbnail_url=video_thumbnail,
                    published_at=video_published
                )
                lst.append(video_info)

            total_results = response['pageInfo']['totalResults']
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return VideoResults(
            total_results=total_results,
            videos=lst
        ).model_dump_json()

    def get_video_info(self, video_ids: str, max_results: int = 50) -> VideoResults:
        """
        Retrieves detailed information about YouTube videos based on the provided video IDs.

        Args:
            video_ids (str): A comma-separated string of video IDs.
            max_results (int): The maximum number of results to return. Default is 50.

        Returns:
            VideoResults: A list of videos with detailed information
        """
        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            request = self.service.videos().list(
                part='id,snippet,contentDetails,statistics,paidProductPlacementDetails,topicDetails', 
                id=video_ids,
                maxResults=min(50, max_results - len(lst)),
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                snippet = item['snippet']
                content_details = item.get('contentDetails', {})
                statistics = item.get('statistics', {})
                topic_details = item.get('topicDetails', {})

                video_info = VideoInfo(
                    channel_id=snippet['channelId'],
                    channel_title=snippet['channelTitle'],
                    video_id=item['id'],
                    video_title=snippet['title'],
                    description=snippet.get('description', ''),
                    # thumbnail_url=snippet['thumbnails']['high']['url'],
                    published_at=snippet['publishedAt'],
                    tags=snippet.get('tags', []),
                    duration=content_details.get('duration'),
                    dimension=content_details.get('dimension'),
                    view_count=statistics.get('viewCount'),
                    like_count=statistics.get('likeCount', 0),
                    comment_count=statistics.get('commentCount', 0),
                    topic_categories=topic_details.get('topicCategories', []),
                    has_paid_product_placement=snippet.get('hasPaidPromotion', False)
                )
                lst.append(video_info)

            total_results = response['pageInfo']['totalResults']
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return VideoResults(
            total_results=total_results,
            videos=lst
        ).model_dump_json()

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> VideoResults:
        """
        Return videos uploaded by a YouTube channel based on the provided channel ID.

        Args:
            channel_id (str): The ID of the YouTube channel.
            max_results (int): The maximum number of results to return. Default is 50.

        Returns:
            VideoResults: A list of videos uploaded by the channel
        """
        lst = []
        total_results = 0
        next_page_token = None

        while len(lst) < max_results:
            request = self.service.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = request.execute()
            # logger.info(f'Fetched {len(response["items"])} videos for channel ID: {channel_id}')

            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists'].get('uploads')

            playlist_request = self.service.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(lst)),
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()

            # video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response.get('items', [])]

            # video_request = self.service.videos().list(
            #     part='snippet,contentDetails,statistics,topicDetails',
            #     id=','.join(video_ids)
            # )
            # video_response = video_request.execute()

            for item in playlist_response['items']:
                snippet = item['snippet']
                # content_details = item.get('contentDetails', {})
                # statistics = item.get('statistics', {})
                # topic_details = item.get('topicDetails', {})

                video_info = VideoInfo(
                    channel_id=snippet['channelId'],
                    channel_title=snippet['channelTitle'],
                    video_id=snippet['resourceId']['videoId'],
                    video_title=snippet['title'],
                    description=snippet.get('description', ''),
                    # thumbnail_url=snippet['thumbnails']['high']['url'],
                    published_at=snippet['publishedAt'],
                    # tags=snippet.get('tags', []),
                    # duration=content_details.get('duration'),
                    # dimension=content_details.get('dimension'),
                    # view_count=statistics.get('viewCount'),
                    # like_count=statistics.get('likeCount', 0),
                    # comment_count=statistics.get('commentCount', 0),
                    # topic_categories=topic_details.get('topicCategories', []),
                    # has_paid_product_placement=snippet.get('hasPaidPromotion', False)
                )
                lst.append(video_info)

            total_results = playlist_response['pageInfo']['totalResults']
            next_page_token = playlist_response.get('nextPageToken')

            if not next_page_token:
                break

        return VideoResults(
            total_results=total_results,
            videos=lst
        ).model_dump_json()
    
    def construct_hyperlinke(self, id: str, type: str) -> str:
        """
        Construct a hyperlink based on the provided ID and type.

        Args:
            id (str): The ID of the YouTube resource.
            type (str): The type of the YouTube resource. Options include 'channel', 'playlist', and 'video'.

        Returns:
            str: The hyperlink to the YouTube resource.
        """
        if type == 'channel':
            return f'https://www.youtube.com/channel/{id}'
        elif type == 'playlist':
            return f'https://www.youtube.com/playlist?list={id}'
        elif type == 'video':
            return f'https://www.youtube.com/watch?v={id}'
        else:
            return ''
