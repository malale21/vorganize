import logging
import re
from pathlib import Path

common_subtitle_exts = ["srt", "sub", "idx", "ssa", "ass", "vtt", "smi", "sami", "stl"]
logger = logging.getLogger(__name__)


def find_subtitle(filename, path, common_subtitle_exts=common_subtitle_exts):
    """Find a subtitle file for the given video filename."""
    base_name = ".".join(filename.split(".")[:-1])  # Remove the extension
    for ext in common_subtitle_exts:
        subtitle_file = f"{base_name}.{ext}"
        if (path / subtitle_file).exists():
            return subtitle_file
    return None

def extract_series_title(filename, pattern):
    """
    Extracts series title and season number from a single filename.
    Returns a tuple: (series_title, season_number) or None if not matched.
    """
    patterns = [
        # e.g. Alice in borderland S03 E05
        r"(?P<title>.+?)\s+[Ss](?P<season>\d{1,2})\s*[Ee]\d{1,2}",
        # e.g. Severance.S02E01
        r"(?P<title>.+?)[. _-]+[Ss](?P<season>\d{1,2})[Ee]\d{1,2}",
    ]
    for pat in patterns:
        m = re.search(pat, filename)
        if m:
            title = m.group("title")
            title = re.sub(r"[._-]+", " ", title).strip()
            season = int(m.group("season"))
            return (title, season)
    return None

