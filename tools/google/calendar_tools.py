import json
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from tools.google.google_apis import GoogleTool, setup_logger

logger = setup_logger('GoogleCalendarTool')

class Calendar(BaseModel):
    """
    Represents a Google Calendar.
    """
    id: str = Field(..., description='Calendar ID')
    name: str = Field(..., description='Calendar name')
    description: Optional[str] = Field(None, description='Calendar description')
    timezone: Optional[str] = Field(None, description='Calendar timezone')

class Calendars(BaseModel):
    """
    Represents a list of Google Calendars.
    """
    calendars: List[Calendar] = Field(..., description='List of Google Calendars')

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


    def create_calendar(self, 
        calendar_name: str,
        timezone: str
    ) -> Dict:
        """
        Creates a new calendar.

        Args:
            calendar_name (str): The name of the new calendar.
            timezone (str): The timezone for the new calendar.
        Returns:
            Dict: A dictionary containing the details of the new calendar.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return None
        
        logger.debug(f"Creating calendar with name: {calendar_name} and timezone: {timezone}")
        try:
            calendar_body = {
                'summary': calendar_name,
                'timeZone': timezone,
            }
            response = self.service.calendars().insert(
                body=calendar_body
            ).execute()

            calendar = {
                'id': response['id'],
                'name': response['summary'],
                'timezone': response['timeZone'],
            }

            logger.info(f"Created new calendar: {calendar_name}")
            return calendar
        
        except Exception as e:
            logger.error(f"An error occurred while creating calendar: {e}")
            return str(e)

    def list_calendars(
        self, 
        show_hidden: Optional[bool] = False,
        show_deleted: Optional[bool] = False,
        limit_total_results: Optional[int] = 100,
    ) -> List[Dict]:
        """
        Lists calendar lists with pagination support.

        Args:
            show_hidden (bool, optional): Whether to include hidden calendars. Default is False.
            show_deleted (bool, optional): Whether to include deleted calendars. Default is False.
            limit_total_results (int, optional): Maximum number of calendars to return. Default is 100.

        Returns:
            List[Dict]: A list of dictionaries containing cleaned calendar information.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return 'service not created'
        
        logger.info(f"Listing calendars with show_hidden={show_hidden}, show_deleted={show_deleted}, limit_total_results={limit_total_results}")

        try:
            # Initialize containers
            all_calendars = []
            all_calendars_cleaned = []
            next_page_token = None
            results_count = 0
            
            while True:
                # Prepare request parameters
                request_params = {
                    'maxResults': min(250, limit_total_results - results_count)
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token

                # Add optional parameters
                if show_hidden:
                    request_params['showHidden'] = show_hidden

                if show_deleted:
                    request_params['showDeleted'] = show_deleted
                
                # Execute API request
                calendar_list = self.service.calendarList().list(**request_params).execute()
                
                # Process results
                calendars = calendar_list.get('items', [])
                all_calendars.extend(calendars)
                results_count += len(calendars)
                
                # Check stopping conditions
                if results_count >= limit_total_results:
                    break
                
                next_page_token = calendar_list.get('nextPageToken')
                if not next_page_token:
                    break
            
            # Clean and format results
            for calendar in all_calendars:
                all_calendars_cleaned.append({
                    'id': calendar['id'],
                    'name': calendar['summary'],
                    'description': calendar.get('description', ''),
                    'timezone': calendar.get('timeZone', ''),
                })
            
            logger.info(f"Retrieved {len(all_calendars_cleaned)} calendars")
            return Calendars(calendars=all_calendars_cleaned)
            
        except Exception as e:
            logger.error(f"An error occurred while listing calendars: {e}")
            return str(e)

    def list_calendar_events(
            self, 
            calendar_id: str = 'primary', 
            show_hidden: Optional[bool] = False, 
            show_deleted: Optional[bool] = False, 
            time_min: Optional[str] = None, 
            time_max: Optional[str] = None,
            limit_total_results: Optional[int] = 20, 
    ) -> List[Dict]:
        """
        Retrieves events from a specified calendar with pagination support.

        Args:
            calendar_id (str): Calendar identifier. Default is 'primary'.
            show_hidden (bool, optional): Whether to include hidden events. Default is False.
            show_deleted (bool, optional): Whether to include deleted events. Default is False.
            time_min (str, optional): Start time as RFC3339 timestamp.
            time_max (str, optional): End time as RFC3339 timestamp.
            limit_total_results (int, optional): Maximum number of events to return in total. Default is 20.

        Returns:
            List[Dict]: A list of event dictionaries.
        """
        if not self.service:
            logger.error("Service not created. Call create_service() first.")
            return 'service not created'
        
        logger.info(f"Listing calendar events with calendar_id={calendar_id}, show_hidden={show_hidden}, show_deleted={show_deleted}, limit_total_results={limit_total_results}")

        try:
            # Initialize containers
            all_events = []
            next_page_token = None
            results_count = 0
            
            while True:
                # Prepare request parameters
                request_params = {
                    'calendarId': calendar_id,
                    'maxResults': min(250, limit_total_results - results_count)
                }
                
                if next_page_token:
                    request_params['pageToken'] = next_page_token

                # Add optional parameters
                if show_hidden:
                    request_params['showHiddenInvitations'] = show_hidden

                if show_deleted:
                    request_params['showDeleted'] = show_deleted
                    
                # Add time filters if provided
                if time_min:
                    request_params['timeMin'] = time_min
                if time_max:
                    request_params['timeMax'] = time_max
                
                # Execute API request
                events_list = self.service.events().list(**request_params).execute()
                
                # Process results
                events = events_list.get('items', [])
                all_events.extend(events)
                results_count += len(events)
                
                # Check stopping conditions
                if results_count >= limit_total_results:
                    all_events = all_events[:limit_total_results]
                    break
                
                next_page_token = events_list.get('nextPageToken')
                if not next_page_token:
                    break
            
            logger.info(f"Retrieved {len(all_events)} events from calendar {calendar_id}")
            return all_events
            
        except Exception as e:
            logger.error(f"An error occurred while listing calendar events: {e}")
            return str(e)
        


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