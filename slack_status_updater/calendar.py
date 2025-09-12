from typing import List, Dict, Optional
from datetime import time as dt_time
from .utils import parse_time, parse_days, is_time_in_range

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def _get_job_for_weekday_hour(intervals: List[Dict], weekday: int, hour: int) -> Optional[Dict]:
    """
    Determine which interval (if any) would apply on a given weekday and hour.
    Behaviour: treat each configured interval as a 'start' event on its allowed days,
    then pick the most recent start (searching backwards through the week) so that
    a status carries forward until replaced. If a job has a time_range, that range
    must include the target time to apply; otherwise it is skipped.
    """
    target_time = dt_time(hour, 0)

    # Build flattened list of starts: (minute_of_week, job)
    starts: List[tuple[int, Dict]] = []
    for job in intervals:
        try:
            allowed_days = parse_days(job["days"])
        except Exception:
            continue
        try:
            t = parse_time(job["time"])
        except Exception:
            continue
        minutes = t.hour * 60 + t.minute
        for d in allowed_days:
            starts.append((d * 1440 + minutes, job))

    if not starts:
        return None

    starts.sort(key=lambda x: x[0])
    target_min = weekday * 1440 + hour * 60

    # find index of last start <= target_min, or wrap to last start
    idx = None
    for i, (m, _) in enumerate(starts):
        if m <= target_min:
            idx = i
    if idx is None:
        idx = len(starts) - 1  # wrap to last start in previous week

    # iterate backwards through starts (circular) and pick first job that is valid for target_time
    n = len(starts)
    for offset in range(n):
        _, job = starts[(idx - offset) % n]

        # If job defines a time_range, the target_time must fall into it
        if "time_range" in job:
            tr = job["time_range"]
            try:
                tr_start = parse_time(tr["start"])
                tr_end = parse_time(tr["end"])
            except Exception:
                # malformed time_range -> skip this candidate
                continue
            if not is_time_in_range(target_time, tr_start, tr_end):
                # this job doesn't cover target_time, keep searching backwards
                continue

        # otherwise this job is considered active (persists) until replaced
        return job

    return None

def _cell_label(job: Optional[Dict], maxlen: int = 12) -> str:
    if not job:
        return "-" * min(3, maxlen)
    emoji = job.get("status_emoji", "") or ""
    text = job.get("status_text", "") or ""
    pres = job.get("presence", "") or ""
    label = emoji if emoji else (text if text else pres)
    label = label.replace(":", "") if label else ""
    label = label.strip()
    if len(label) > maxlen:
        return label[: maxlen - 1] + "…"
    return label or "-"

def render_week_calendar(intervals: List[Dict]) -> str:
    """
    Render a compact week calendar: rows are hours 00-23, columns are Mon..Sun.
    Each cell shows a short label (emoji / status_text / presence).
    """
    col_width = 14
    hour_col_width = 6
    header = " " * hour_col_width
    for d in DAY_NAMES:
        header += d.center(col_width)
    lines = [header, "-" * (hour_col_width + col_width * 7)]

    for hour in range(24):
        hour_label = f"{hour:02d}:00".rjust(hour_col_width)
        row = hour_label
        for wd in range(7):
            job = _get_job_for_weekday_hour(intervals, wd, hour)
            cell = _cell_label(job, maxlen=col_width - 2)
            row += cell.center(col_width)
        lines.append(row)

    lines.append("")  # blank line
    lines.append("Legend: cell shows (emoji) or status_text or presence. '-' = no interval")
    return "\n".join(lines)
