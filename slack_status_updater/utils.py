from datetime import datetime
from typing import List, Union

def parse_time(timestr: str) -> datetime.time:
    """
    Parse a time string in HH:MM format.
    """
    try:
        return datetime.strptime(timestr, "%H:%M").time()
    except ValueError:
        raise ValueError(f"Invalid time format for '{timestr}', expected HH:MM")

def parse_days(days: Union[str, List[str]]) -> List[int]:
    """
    Parse days specification and return list of weekday numbers (0=Monday, 6=Sunday).
    
    Args:
        days: String like "weekdays", "weekends", or list of day names
        
    Returns:
        List of weekday numbers
    """
    day_names = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6
    }
    
    if isinstance(days, str):
        days_lower = days.lower()
        if days_lower == "weekdays":
            return [0, 1, 2, 3, 4]  # Monday to Friday
        elif days_lower == "weekends":
            return [5, 6]  # Saturday and Sunday
        elif days_lower in day_names:
            return [day_names[days_lower]]
        else:
            raise ValueError(f"Invalid day specification: '{days}'. Use 'weekdays', 'weekends', or day names.")
    
    elif isinstance(days, list):
        result = []
        for day in days:
            if isinstance(day, str):
                day_lower = day.lower()
                if day_lower in day_names:
                    result.append(day_names[day_lower])
                else:
                    raise ValueError(f"Invalid day name: '{day}'. Use day names like 'monday', 'tuesday', etc.")
            else:
                raise ValueError(f"Day must be a string, got {type(day)}")
        return result
    
    else:
        raise ValueError(f"Days must be a string or list of strings, got {type(days)}")

def is_time_in_range(current_time: datetime.time, start_time: datetime.time, end_time: datetime.time) -> bool:
    """
    Check if current_time is within the range [start_time, end_time).
    Handles cases where the range crosses midnight.
    """
    if start_time <= end_time:
        # Normal range (e.g., 09:00 to 17:00)
        return start_time <= current_time < end_time
    else:
        # Range crosses midnight (e.g., 22:00 to 06:00)
        return current_time >= start_time or current_time < end_time

def is_day_match(current_weekday: int, allowed_days: List[int]) -> bool:
    """
    Check if current weekday matches any of the allowed days.
    
    Args:
        current_weekday: Current day of week (0=Monday, 6=Sunday)
        allowed_days: List of allowed weekdays
    """
    return current_weekday in allowed_days
