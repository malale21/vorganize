from pathlib import Path
import json
import logging
from .core import find_subtitle
"""_summary_:
Save video metadata to JSON files.
This module provides functionality to store video metadata in JSON files for Movies, TV Shows, and Other Videos.
It handles the creation of directories, checks for existing files, and appends new entries as needed.
"""

logger = logging.getLogger(__name__)

def store_as_json(video_type, data, json_file):
    """Store video metadata in JSON files."""
    file_type = {"s": "shows", "m": "movies", "o": "videos"}[video_type]
    json_path = Path(json_file)
    json_data = {file_type: [], f"{file_type}_subtitles": []}
    if json_path.exists():
        with open(json_path, "r") as f:
            json_data = json.load(f)
        if file_type not in json_data:
            json_data[file_type] = []
        if f"{file_type}_subtitles" not in json_data:
            json_data[f"{file_type}_subtitles"] = []
        if file_type == "shows" and isinstance(json_data[file_type], dict):
            json_data[file_type] = sorted(json_data[file_type].keys())

    item_to_add = data[0] if video_type == "s" else data
    if item_to_add not in json_data[file_type]:
        json_data[file_type].append(item_to_add)
        json_data[file_type].sort()

    subtitle_file = data[2] if video_type == "s" else find_subtitle(data, json_path.parent)
    if subtitle_file and subtitle_file not in json_data[f"{file_type}_subtitles"]:
        json_data[f"{file_type}_subtitles"].append(subtitle_file)
        json_data[f"{file_type}_subtitles"].sort()

    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=4)