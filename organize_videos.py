import re
import json
import shutil
import logging
from pathlib import Path
from collections import defaultdict
import colorama
from colorama import Fore, Style

# Initialize colorama for colored output
colorama.init()

# Custom logging formatter for colored console output
class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            return Fore.GREEN + super().format(record) + Style.RESET_ALL
        elif record.levelno == logging.WARNING:
            return Fore.YELLOW + super().format(record) + Style.RESET_ALL
        elif record.levelno == logging.ERROR:
            return Fore.RED + super().format(record) + Style.RESET_ALL
        return super().format(record)

# Set up logging with console handler and colored output
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter('%(message)s'))
logger.addHandler(console_handler)

# Define source and destination directories (update these paths)
source_dir = "/home/malale/dump/test-files"  # Update to your source directory
dest_dir = "/home/malale/dump/"  # Update to your destination directory
path = Path(source_dir)
video_ext = ['mp4', 'avi', 'mkv', 'mov', 'wmv']

# Regex patterns for series and movies (case-insensitive)
series_pattern = re.compile(r"S\d{1,2}E\d{1,2}", re.IGNORECASE)
movie_pattern = re.compile(r".*\(\d{4}\).*", re.IGNORECASE)

# Function to extract series title from filename
def extract_series_title(filename):
    match = series_pattern.search(filename)
    if match:
        return filename[:match.start()].strip().rstrip('.')
    return None

# Categorize files
series_dict = defaultdict(list)
movies = []
other_videos = []

for item in path.iterdir():
    if item.is_file() and item.suffix[1:].lower() in video_ext:
        if series_pattern.search(item.name):
            series_title = extract_series_title(item.name)
            if series_title:
                series_dict[series_title].append(item.name)
        elif movie_pattern.search(item.name):
            movies.append(item.name)
        else:
            other_videos.append(item.name)

# Sort the lists
for episodes in series_dict.values():
    episodes.sort()
movies.sort()
other_videos.sort()

# Define destination paths
shows_dest = str(Path(dest_dir) / "tv-shows")
movies_dest = str(Path(dest_dir) / "movies")
others_dest = str(Path(dest_dir) / "other_videos")

# Create destination directories
Path(shows_dest).mkdir(exist_ok=True)
Path(movies_dest).mkdir(exist_ok=True)
Path(others_dest).mkdir(exist_ok=True)

# Move series episodes
for series_title, episodes in series_dict.items():
    series_dir = Path(shows_dest) / series_title
    series_dir.mkdir(exist_ok=True)
    for episode in episodes:
        source = path / episode
        dest = series_dir / episode
        if dest.exists():
            logger.warning(f"Skipping {episode}: {dest} already exists.")
        else:
            shutil.move(str(source), str(dest))
            logger.info(f"Moved {episode} to {series_dir}")

# Move movies
for movie in movies:
    source = path / movie
    dest = Path(movies_dest) / movie
    if dest.exists():
        logger.warning(f"Skipping {movie}: {dest} already exists.")
    else:
        shutil.move(str(source), str(dest))
        logger.info(f"Moved {movie} to {movies_dest}")

# Move other videos
for video in other_videos:
    source = path / video
    dest = Path(others_dest) / video
    if dest.exists():
        logger.warning(f"Skipping {video}: {dest} already exists.")
    else:
        shutil.move(str(source), str(dest))
        logger.info(f"Moved {video} to {others_dest}")

# Prepare data for JSON
shows_data = {
    "from": source_dir,
    "to": shows_dest,
    "shows": {title: sorted(episodes) for title, episodes in series_dict.items()}
}
movies_data = {
    "from": source_dir,
    "to": movies_dest,
    "movies": sorted(movies)
}
others_data = {
    "from": source_dir,
    "to": others_dest,
    "videos": sorted(other_videos)
}

# Save to JSON files
with open("shows.json", "w") as file:
    json.dump(shows_data, file, indent=2)
with open("movies.json", "w") as file:
    json.dump(movies_data, file, indent=2)
with open("other_videos.json", "w") as file:
    json.dump(others_data, file, indent=2)

logger.info("File organization complete!")