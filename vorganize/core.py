from pathlib import Path
import re
import logging

common_subtitle_exts = ["srt", "sub", "idx", "ssa", "ass", "vtt", "smi", "sami", "stl"]
logger = logging.getLogger(__name__)

def find_subtitle(filename, path, common_subtitle_exts=common_subtitle_exts):
    """Find a subtitle file for the given video filename."""
    base_name = '.'.join(filename.split('.')[:-1])  # Remove the extension
    for ext in common_subtitle_exts:
        subtitle_file = f"{base_name}.{ext}"
        if (path / subtitle_file).exists():
            return subtitle_file
    return None

def extract_series_title(filename, series_pattern):
    """Extract series title and season number from filename."""
    match = series_pattern.search(filename)
    if match:
        try:
            season_number = int(match.group(1))  # Extract season from capture group
            series_title = filename[:match.start()].strip().rstrip('.')
            logger.debug(f"Extracted series '{series_title}' with season {season_number} from '{filename}'", extra={"indent": 4})
            return series_title, season_number
        except (IndexError, ValueError):
            logger.warning(f"Failed to extract season number from '{filename}' (matched pattern but no valid season).", extra={"indent": 4})
            return filename[:match.start()].strip().rstrip('.'), None
    logger.debug(f"No series pattern match for '{filename}'", extra={"indent": 4})
    return None, None