from typing import Dict, List, Optional


def fmt_duration(seconds: float) -> str:
    """4.2 -> '4.2s', 75 -> '1m 15s', 3725 -> '1h 02m'."""
    seconds = max(0.0, seconds)
    if seconds < 10:
        return f"{seconds:.1f}s"
    s = int(round(seconds))
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s:02d}s"
    h, m = divmod(m, 60)
    return f"{h}h {m:02d}m"


def reply_durations(messages: List[Dict]) -> List[Optional[float]]:
    """For each message, how long the reply took: the assistant message's time minus the time of
    the user prompt before it (both are saved by the store). None for user messages or when unknown."""
    out: List[Optional[float]] = []
    asked: Optional[float] = None
    for m in messages:
        ts = m.get("ts")
        if m.get("role") == "user":
            asked = ts if isinstance(ts, (int, float)) else None
            out.append(None)
        elif asked is not None and isinstance(ts, (int, float)) and ts >= asked:
            out.append(ts - asked)
            asked = None
        else:
            out.append(None)
    return out
