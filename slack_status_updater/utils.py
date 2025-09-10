from datetime import datetime

def parse_time(timestr: str) -> datetime.time:
    """
    Parse a time string in HH:MM format.
    """
    try:
        return datetime.strptime(timestr, "%H:%M").time()
    except ValueError:
        raise ValueError(f"Invalid time format for '{timestr}', expected HH:MM")
