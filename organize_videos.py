import re, os, argparse
import json
import shutil
import logging
import textwrap
from pathlib import Path
from collections import defaultdict
import colorama
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

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

# Custom help formatter for argparse
class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = f"{Fore.CYAN}Usage:{Style.RESET_ALL} "
        return super().add_usage(usage, actions, groups, prefix)

video_ext = ['mp4', 'avi', 'mkv', 'mov', 'wmv']

# Script config directory
script_dir = '/home/malale/.local/movies_script/'

# json file to store filenames
movies_json = f"{script_dir}movies.json"
shows_json = f"{script_dir}shows.json"
other_videos_json = f"{script_dir}other_videos.json"


# Regex patterns for series and movies (case-insensitive), Used more movie patterns because it's hard to match movies with one pattern
series_pattern = re.compile(r"S\d{1,2}E\d{1,2}", re.IGNORECASE)
movie_pattern = re.compile(r".*\(\d{4}\).*", re.IGNORECASE)
movie_pattern2 = re.compile(r'^[\w\s\-\.]+?\.\d{4}\.?(?:720p|1080p)?\.?(?:BluRay|WEBRip|WEB-DL|BrRip)?\.?(?:x264|x265|HEVC|AAC)?\.?(?:6CH|DDP5\.1|10bit)?\.?(?:[\w\-\.\[\]]+)?\.(?:mkv|mp4)$')
movie_pattern3 = re.compile(r'^[\w\s\-\.]+_\d{4}_[\w\-\.]+?\.(?:mkv|mp4)$')

# Function to extract series title from filename
def extract_series_title(filename):
    match = series_pattern.search(filename)
    if match:
        return filename[:match.start()].strip().rstrip('.')
    return None


# Function to handle intercative
def handle_inter(source, videos, dest_dict):
    user_series_dict = {}
    user_vid_list = []
    user_movie_list = []
    

    for filename in videos:
        new_name = input(f"{Fore.CYAN}Enter new name for '{filename}' Without the extention (press Enter to keep): {Style.RESET_ALL}")
        if new_name:
            new_name = new_name + f'.{filename.split(".")[-1]}'
            try:
                os.rename(
                os.path.join(source, filename),
                os.path.join(source, new_name)
                )
                logger.info(f"Renamed '{filename}' to '{new_name}'")
            except OSError as e:
                logger.error(f"Failed to rename '{filename}': {e}")
        else:
            new_name = filename
            
        while True:
            category = input(f"{Fore.CYAN}Categorize '{new_name}' (m=movies, s=tv-shows, o=other): {Style.RESET_ALL}").lower()
            if category in dest_dict:
                break
            logger.error(f"Invalid input '{category}'. Please enter m, s, or o.")
        
        if category == "s":
            series_title = extract_series_title(new_name)
            series_title = series_title.replace('.', ' ')
            if series_title:
                user_series_dict[series_title].append(filename)
                store_as_json("s", series_title)
        elif category == "m":
            user_movie_list.append(new_name)
            store_as_json(category, new_name)
    move_series(user_series_dict, source, dest_dict["s"]) # To move shows
    move_items(user_movie_list, source, dest_dict["m"]) # To show movies
    move_items(user_vid_list, source, dest_dict["o"]) # To move other videos

# Function to store organized files as a json
def store_as_json(video_type, filename):
    file_type = "shows" if video_type == "s" else "movies" if video_type == "m" else "other_vids"
    json_file = shows_json if video_type == "s" else movies_json if video_type == "m" else other_videos_json
    if os.path.exists(json_file):
        with open(json_file, "r") as f:
            data = json.load(f)
        # Ensure data is a dictionary with file_type as key
        if not isinstance(data, dict):
            data = {file_type: data} if isinstance(data, list) else {file_type: []}
        if file_type not in data or not isinstance(data[file_type], list):
            data[file_type] = []
        # Check if the filename already exists in the list
        if filename not in data[file_type]:
            data[file_type].append(filename)
            # Sort the list for consistency
            data[file_type] = sorted(data[file_type])
            with open(json_file, "w") as f:
                json.dump(data, f, indent=4)
    else:
        # If the JSON file does not exist, create it with the new filename
        data = {file_type: [filename]}
        print(f"{json_file} does not exist. Creating new file.")
        with open(json_file, "w") as f:
            json.dump(data, f, indent=4)

# Categorize files
series_dict = defaultdict(list)
movies = []
other_videos = []
# To move series
def move_series(series_dict, path, dest_dir):
    for series_title, episodes in series_dict.items():
        series_dir = Path(dest_dir) / series_title
        series_dir.mkdir(exist_ok=True)
        for episode in episodes:
            source = path / episode
            dest = series_dir / episode
            if dest.exists():
                logger.warning(f"Skipping {episode}: {dest} already exists.")
            else:
                shutil.move(str(source), str(dest))
                logger.info(f"Moved {episode} to {series_dir}")
    
# To move files other than series
def move_items(video_list, path, dest_dir):
    for filename  in video_list:
        
        source = path / filename
        dest = Path(dest_dir) / filename
        if dest.exists():
            logger.warning(f"Skipping {filename}: {dest} already exists.")
        else:
            shutil.move(str(source), str(dest))
            logger.info(f"Moved {filename} to {dest}")
    

            
# To prepare the lists of files to move
def prepare_lists(filename):
    if series_pattern.search(filename):
        series_title = extract_series_title(filename)
        # Repalce dots with spaces if they exist in series_title
        series_title = series_title.replace('.', ' ')
        # Add the file to the series dictionary under the series title
        if series_title:
            series_dict[series_title].append(filename)
            store_as_json("s", series_title)
    elif movie_pattern.search(filename):
        print(f"Match : {filename}")
        movies.append(filename)
        store_as_json("m", filename)
    elif movie_pattern2.search(filename):
        movies.append(filename)
        print(f"Match : {filename}")
        store_as_json("m", filename)
    elif movie_pattern3.search(filename):
        print(f"Match : {filename}")
        movies.append(filename)
        store_as_json("m", filename)
    else:
        print(f"Other : {filename}")
        other_videos.append(filename)
        store_as_json("o", filename)
    
    
def main(path,dest_dir,interactive):
    for item in path.iterdir():
        if item.is_file() and item.suffix[1:].lower() in video_ext:
            prepare_lists(item.name) 
            
    # Define destination paths
    shows_dest = str(Path(dest_dir) / "shows")
    movies_dest = str(Path(dest_dir) / "Movies")
    others_dest = str(Path(dest_dir) / "other_videos")

    # Create destination directories
    Path(shows_dest).mkdir(exist_ok=True)
    Path(movies_dest).mkdir(exist_ok=True)
    Path(others_dest).mkdir(exist_ok=True)
    
    category_map = {
        'm': movies_dest,
        's': shows_dest,
        'o': others_dest
        }
    # Sort the lists
    for episodes in series_dict.values():
        episodes.sort()
    movies.sort()
    other_videos.sort()
    # move_items(video_list, source, dest_dir, video_type):
    move_items(movies, path, movies_dest) # To move movies
    move_series(series_dict, path, shows_dest) # To move shows
    if interactive:
        handle_inter(path, other_videos, category_map)
    else :
        move_items(other_videos, path, others_dest) # To move other videos
    #logger.info("File organization complete!")

# If i wanted to store the episodes with series title as a json 
# shows_data = {
#     "from": source_dir,
#     "to": shows_dest,
#     "shows": {title: sorted(episodes) for title, episodes in series_dict.items()}
# }

 #Set up the parser
parser = argparse.ArgumentParser(
    description=textwrap.dedent(f"""
    {Fore.CYAN}🎥 Video File Organizer 🎥{Style.RESET_ALL}
    Sort your video files into Movies, TV Shows, and Other Videos with ease!
    Move files from a source directory to a destination directory, with optional
    interactive renaming. 🚀
    """),
    formatter_class=CustomHelpFormatter,
    epilog=f"{Fore.MAGENTA}Example: python3 organize_videos.py -s ~/videos -d ~/organized -i    {Style.RESET_ALL}"
)
# Validate directory paths
def valid_dir(path):
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(f"{Fore.RED}Invalid directory: {path}{Style.RESET_ALL}")
    return path

# Define arguments concisely
args_config = [
    {
        'flags': ['-s', '--source'],
        'required': True,
        'metavar': 'DIR',
        'type': valid_dir,
        'help': 'Source directory containing video files 📂'
    },
    {
        'flags': ['-d', '--dest'],
        'required': True,
        'metavar': 'DIR',
        'type': valid_dir,
        'help': 'Destination directory to organize files into 📁'
    },
    {
        'flags': ['-i', '--interactive'],
        'action': 'store_true',
        'help': 'Enable interactive mode to rename files during processing ✍️'
    }
]

# Add arguments dynamically
for arg in args_config:
    parser.add_argument(*arg['flags'], **{k: v for k, v in arg.items() if k != 'flags'})

# Parse arguments
args = parser.parse_args()

if __name__ == "__main__":    
    source_dir = args.source
    dest_dir = args.dest
    path = Path(source_dir)
    main(path, dest_dir, args.interactive)
    
    
    