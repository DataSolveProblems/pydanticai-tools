from typing import List, Optional, Dict, Any, Union
import json
from tools.google.google_apis import GoogleTool, setup_logger

logger = setup_logger('GoogleCalendarTool')

class GoogleCalendarTool(GoogleTool):
    """
    A concrete implementation of GoogleTool for Google Calendar API.
    """
    def __init__(self, client_secret_file):
        # Define specific parameters for Google Calendar API
        super().__init__(
            client_secret_file=client_secret_file,
            api_name='calendar',
            api_version='v3',
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        self.create_service()

    def create_service(self):
        """
        Implements the abstract method to create a Google Calendar service.
        """
        return super().create_service()

    @property
    def get_service(self):
        """
        Returns the Google Calendar service instance.
        """
        if self.service:
            return self.service
        else:
            logger.error("Service not created. Call create_service() first.")
            return None

    def list_events(self, 
            calendar_id='primary', 
            total_results=10, 
            show_hidden=False, 
            show_deleted=False, 
            time_min=None, 
            time_max=None
    ) -> List[Dict]:
            """
            Retrieves events from a specified calendar with pagination support.

            Args:
                calendar_id (str): Calendar identifier. Default is 'primary'.
                total_results (int, optional): Maximum number of events to return in total.
                show_hidden (bool): Whether to include hidden events. Default is False.
                show_deleted (bool): Whether to include deleted events. Default is False.
                time_min (str, optional): Start time as RFC3339 timestamp.
                time_max (str, optional): End time as RFC3339 timestamp.

            Returns:
                List[Dict]: A list of event dictionaries.
            """
            if not self.service:
                logger.error("Service not created. Call create_service() first.")
                return None

            # Initialize request parameters
            request_params = {
                'calendarId': calendar_id,
                'maxResults': min(250, total_results if total_results else 250),
                'showHiddenInvitations': show_hidden,
                'showDeleted': show_deleted,
            }
            
            # Add time filters if provided
            if time_min:
                request_params['timeMin'] = time_min
            if time_max:
                request_params['timeMax'] = time_max

            # Fetch events with pagination
            events = []
            page_token = None
            
            while True:
                # Update page token for subsequent requests
                if page_token:
                    request_params['pageToken'] = page_token
                    
                # Execute API request and collect events
                results = self.service.events().list(**request_params).execute()
                current_events = results.get('items', [])
                events.extend(current_events)
                
                # Check stopping conditions
                page_token = results.get('nextPageToken')
                if total_results and len(events) >= total_results:
                    events = events[:total_results]
                    break
                if not page_token:
                    break

            logger.info(f"Retrieved {len(events)} events from calendar {calendar_id}")
            return events

    def create_calendar(self, calendar_name: str) -> Dict:
        """
        Creates a new calendar.

        Args:
            calendar_name (str): The name of the new calendar.

        Returns:
            Dict: A dictionary containing the details of the new calendar.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return None
        
        try:
            calendar_body = {
                'summary': calendar_name
            }
            created_calendar = self.service.calendars().insert(
                body=calendar_body
            ).execute()
            logger.info(f"Created new calendar: {calendar_name}")
            return created_calendar
        except Exception as e:
            logger.error(f"An error occurred while creating calendar: {e}")
            return None

    def list_calendars(self, max_results: Union[int, str] = 200) -> List[Dict]:
        """
        Lists calendar lists with pagination support.

        Args:
            max_results (int or str, optional): Maximum number of calendars to retrieve.
                Defaults to 200. If a string is provided, it will be converted to an integer.

        Returns:
            List[Dict]: A list of dictionaries containing cleaned calendar information.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return None
        
        try:
            # Convert max_results to integer if it's a string
            if isinstance(max_results, str):
                max_results = int(max_results)
            
            # Initialize containers
            all_calendars = []
            all_calendars_cleaned = []
            page_token = None
            results_count = 0
            
            while True:
                # Prepare request parameters
                request_params = {
                    'maxResults': min(250, max_results - results_count)
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                # Execute API request
                calendar_list = self.service.calendarList().list(
                    **request_params
                ).execute()
                
                # Process results
                calendars = calendar_list.get('items', [])
                all_calendars.extend(calendars)
                results_count += len(calendars)
                
                # Check stopping conditions
                if results_count >= max_results:
                    break
                page_token = calendar_list.get('nextPageToken')
                if not page_token:
                    break
            
            # Clean and format results
            for calendar in all_calendars:
                all_calendars_cleaned.append({
                    'id': calendar['id'],
                    'name': calendar['summary'],
                    'description': calendar.get('description', '')
                })
            
            logger.info(f"Retrieved {len(all_calendars_cleaned)} calendars")
            return all_calendars_cleaned
            
        except Exception as e:
            logger.error(f"An error occurred while listing calendars: {e}")
            return None

    def list_calendar_events(
            self, 
            calendar_id: str, 
            max_results: Union[int, str] = 20
    ) -> List[Dict]:
        """
        Lists events from a specified calendar with pagination support.

        Args:
            calendar_id (str): The ID of the calendar from which to list events.
            max_results (int or str, optional): Maximum number of events to retrieve.
                Defaults to 20. If a string is provided, it will be converted to an integer.

        Returns:
            List[Dict]: A list of events from the specified calendar.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return None
        
        try:
            # Convert max_results to integer if it's a string
            if isinstance(max_results, str):
                max_results = int(max_results)
            
            # Initialize containers
            all_events = []
            page_token = None
            results_count = 0
            
            while True:
                # Prepare request parameters
                request_params = {
                    'calendarId': calendar_id,
                    'maxResults': min(250, max_results - results_count)
                }
                
                if page_token:
                    request_params['pageToken'] = page_token
                
                # Execute API request
                events_list = self.service.events().list(**request_params).execute()
                
                # Process results
                events = events_list.get('items', [])
                all_events.extend(events)
                results_count += len(events)
                
                # Check stopping conditions
                if results_count >= max_results:
                    break
                page_token = events_list.get('nextPageToken')
                if not page_token:
                    break
            
            logger.info(f"Retrieved {len(all_events)} events from calendar {calendar_id}")
            return all_events
            
        except Exception as e:
            logger.error(f"An error occurred while listing calendar events: {e}")
            return None

    def insert_calendar_event(
            self, 
            calendar_id: str, 
            event_data: Dict[str, Any]
    ) -> Dict:
        """
        Inserts an event into the specified calendar.

        Args:
            calendar_id (str): The ID of the calendar where the event will be inserted.
            event_data (Dict[str, Any]): Dictionary containing the event details.

        Returns:
            Dict: The created event details.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return None
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            logger.info(f"Created event in calendar {calendar_id}")
            return event
        except Exception as e:
            logger.error(f"An error occurred while creating event: {e}")
            return None