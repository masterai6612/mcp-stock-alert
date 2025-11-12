"""
Timezone Utilities
Provides consistent timezone handling across the application
"""

from datetime import datetime
import pytz

# Define EST timezone
EST = pytz.timezone('America/New_York')

def get_local_time():
    """Get current time in EST timezone"""
    return datetime.now(EST)

def format_timestamp(dt=None, format_str='%Y-%m-%d %H:%M:%S %Z'):
    """Format timestamp in EST timezone"""
    if dt is None:
        dt = get_local_time()
    elif dt.tzinfo is None:
        # If naive datetime, assume UTC and convert to EST
        dt = pytz.UTC.localize(dt).astimezone(EST)
    return dt.strftime(format_str)

def get_local_now_str(format_str='%Y-%m-%d %H:%M:%S EST'):
    """Get current time as formatted string in EST"""
    return get_local_time().strftime(format_str)

def get_local_isoformat():
    """Get current time in ISO format with EST timezone"""
    return get_local_time().isoformat()
