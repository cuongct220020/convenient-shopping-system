from datetime import datetime, timezone, timedelta

def get_current_timestamp() -> str:
    """Get current timestamp in custom format (MM-DD-YYYY HH:MM:SS +07)."""
    vietnam_tz = timezone(timedelta(hours=7))
    now = datetime.now(vietnam_tz)
    return now.strftime("%m-%d-%Y %H:%M:%S +07")