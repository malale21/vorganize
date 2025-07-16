import re, json
from pathlib import Path
from collections import Counter

# Define the directory and video extensions
#directory_path = "/home/malale/Downloads/Telegram Desktop/"
directory_path = "/home/malale/dump/test-files"
destination = "/home/malale/dump/"
path = Path(directory_path)
video_ext = ['mp4', 'avi', 'mkv', 'mov', 'wmv']

# Function to extract series title from filename
def extract_series_title(filename):
    match = series_pattern.search(filename)
    if match:
        return filename[:match.start()].strip().rstrip('.')
    return None

def extract_movie_title(filename):
    match = series_pattern.search(filename)
    if match:
        return filename[:match.start()].strip().rstrip('.')
    return None

# Regex patterns for movies and series
movie_pattern = re.compile(r".*\(\d{4}\).*")  # Matches titles with a year, e.g., "Movie (2020)"
series_pattern = re.compile(r".*S\d{1,2}E\d{1,2}.*")  # Matches "S01E01" style, e.g., "Series S01E01"

# Lists to store categorized files
movies = []
series = []
other_videos = []

# Iterate through the directory
for item in path.iterdir():
    if item.is_file() and item.suffix[1:].lower() in video_ext:  # Check if it's a video file
        if movie_pattern.search(item.name):
            
            movies.append(item.name)
        elif series_pattern.search(item.name):
            series.append(item.name)
        else:
            other_videos.append(item.name)
series.sort()
movies.sort()
other_videos.sort()
shows_data = {
    "from":directory_path,
    "to": destination + "tv-shows",
    "shows": series
}
movies_data = {
    "from":directory_path,
    "to": destination + "movies",
    "movies" : movies
}
others_data = {
    "from":directory_path,
    "to": destination + "movies",
    "videos" : other_videos
}
with open("movies.json","w") as file:
    json.dump(movies_data, file, indent=2)
with open("shows.json","w") as file:
    json.dump(shows_data, file, indent=2)
with open("other_vids.json","w") as file:
    json.dump(others_data, file, indent=2)
