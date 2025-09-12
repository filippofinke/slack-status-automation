import os
from typing import Any, Dict, List, Optional
import yaml

class ConfigError(Exception):
    """Custom exception for configuration errors."""
    pass

def load_config(path: str = "config.yml") -> Dict[str, Any]:
    """
    Load YAML configuration from `path`.
    If the file does not exist, a `ConfigError` is raised.
    """
    if not os.path.exists(path):
        raise ConfigError(f"Config file '{path}' not found.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_slack_token(config: Dict[str, Any]) -> Optional[str]:
    """
    Return Slack token from environment variable or config dictionary.
    Environment variable `SLACK_TOKEN` takes precedence.
    """
    return os.environ.get("SLACK_TOKEN") or config.get("slack_token")

def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate `config` and raise `ConfigError` if invalid.
    """
    errors: List[str] = []

    if not get_slack_token(config):
        errors.append("Missing Slack token: set SLACK_TOKEN or add 'slack_token' to config.yml")

    intervals = config.get("intervals")
    if intervals is None:
        errors.append("Missing 'intervals' section in config.yml")
    elif not isinstance(intervals, list) or not intervals:
        errors.append("'intervals' must be a non-empty list")
    else:
        for i, item in enumerate(intervals):
            if not isinstance(item, dict):
                errors.append(f"intervals[{i}] must be a mapping")
                continue
            
            # Validate time field
            if "time" not in item:
                errors.append(f"intervals[{i}] missing required 'time' (HH:MM)")
            else:
                try:
                    from .utils import parse_time
                    parse_time(item["time"])
                except ValueError:
                    errors.append(f"intervals[{i}].time has invalid format, expected HH:MM")
            
            # Validate days field (required)
            if "days" not in item:
                errors.append(f"intervals[{i}] missing required 'days' field")
            else:
                try:
                    from .utils import parse_days
                    parse_days(item["days"])
                except ValueError as e:
                    errors.append(f"intervals[{i}].days: {e}")
            
            # Validate time_range field (optional)
            if "time_range" in item:
                time_range = item["time_range"]
                if not isinstance(time_range, dict):
                    errors.append(f"intervals[{i}].time_range must be a mapping with 'start' and 'end'")
                else:
                    if "start" not in time_range:
                        errors.append(f"intervals[{i}].time_range missing required 'start' (HH:MM)")
                    else:
                        try:
                            from .utils import parse_time
                            parse_time(time_range["start"])
                        except ValueError:
                            errors.append(f"intervals[{i}].time_range.start has invalid format, expected HH:MM")
                    
                    if "end" not in time_range:
                        errors.append(f"intervals[{i}].time_range missing required 'end' (HH:MM)")
                    else:
                        try:
                            from .utils import parse_time
                            parse_time(time_range["end"])
                        except ValueError:
                            errors.append(f"intervals[{i}].time_range.end has invalid format, expected HH:MM")

    if errors:
        raise ConfigError("\\n".join(errors))
