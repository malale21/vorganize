#!/usr/bin/env python3

import argparse
import textwrap
from pathlib import Path
import re, os
from collections import defaultdict
import logging
import colorama
from colorama import Fore, Style
from vorganize import prepare_lists, move_series, move_items, handle_inter

# Custom logging formatter
class CustomFormatter(logging.Formatter):
    def format(self, record):
        indent = "  " * getattr(record, "indent", 0)
        if record.levelno == logging.INFO:
            return f"{indent}{Fore.GREEN}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.WARNING:
            return f"{indent}{Fore.YELLOW}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.ERROR:
            return f"{indent}{Fore.RED}{record.msg}{Style.RESET_ALL}"
        elif record.levelno == logging.DEBUG:
            return f"{indent}{Fore.BLUE}{record.msg}{Style.RESET_ALL}"
        return f"{indent}{record.msg}"

# Set up logging
colorama.init(autoreset=True)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Changed to DEBUG to show debug logs
console_handler = logging.StreamHandler()
console_handler.setFormatter(CustomFormatter())
logger.handlers = [console_handler]

# Custom help formatter for argparse
class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = f"{Fore.CYAN}Usage:{Style.RESET_ALL} "
        return super().add_usage(usage, actions, groups, prefix)

def main(path, dest_dir, interactive, script_dir="/home/malale/.local/movies_script/"):
    path = Path(path)
    dest_dir = Path(dest_dir)
    series_dict = defaultdict(lambda: defaultdict(list))
    movies = []
    other_videos = []
    
    # File patterns and subtitle extensions
    video_ext = ['mp4', 'avi', 'mkv', 'mov', 'wmv']
    common_subtitle_exts = ["srt", "sub", "idx", "ssa", "ass", "vtt", "smi", "sami", "stl"]
    series_pattern = re.compile(r"(?i)(?:S|Season\s*)(\d{1,2})(?:E|Episode\s*|\.|-|x)\d{1,2}", re.IGNORECASE)
    movie_pattern = re.compile(r".*\(\d{4}\).*", re.IGNORECASE)
    movie_pattern2 = re.compile(r'^[\w\s\-\.]+?\.\d{4}\.?(?:720p|1080p)?\.?(?:BluRay|WEBRip|WEB-DL|BrRip)?\.?(?:x264|x265|HEVC|AAC)?\.?(?:6CH|DDP5\.1|10bit)?\.?(?:[\w\-\.\[\]]+)?\.(?:mkv|mp4)$')
    movie_pattern3 = re.compile(r'^[\w\s\-\.]+_\d{4}_[\w\-\.]+?\.(?:mkv|mp4)$')
    
    # JSON file paths
    movies_json = str(Path(script_dir) / "movies.json")
    shows_json = str(Path(script_dir) / "shows.json")
    other_videos_json = str(Path(script_dir) / "other_videos.json")
    
    # Category mapping
    category_map = {
        "s": dest_dir / "shows",
        "m": dest_dir / "Movies",
        "o": dest_dir / "other_videos"
    }
    
    # Create destination directories
    for dest in category_map.values():
        dest.mkdir(parents=True, exist_ok=True)
    
    # Process files
    logger.info(f"Scanning directory: {path}", extra={"indent": 0})
    for item in path.iterdir():
        if item.is_file() and item.suffix[1:].lower() in video_ext:
            prepare_lists(item.name, path, series_dict, movies, other_videos, series_pattern, movie_pattern, movie_pattern2, movie_pattern3, common_subtitle_exts, shows_json, movies_json, other_videos_json)

    # Sort lists
    for series_title in series_dict:
        for season in series_dict[series_title]:
            series_dict[series_title][season].sort(key=lambda x: x[0])
    movies.sort(key=lambda x: x[0])
    other_videos.sort(key=lambda x: x[0])

    # Move files
    move_series(series_dict, path, category_map["s"])
    move_items(movies, path, category_map["m"], item_type="movies")
    if interactive:
        handle_inter(path, other_videos, category_map, series_pattern, common_subtitle_exts)
    else:
        move_items(other_videos, path, category_map["o"], item_type="videos")

    # Final summary
    total_series = len(series_dict)
    total_episodes = sum(len(episodes) for series in series_dict.values() for episodes in series.values())
    total_movies = len(movies)
    total_others = len(other_videos)
    logger.info(f"Summary: Processed {total_series} series ({total_episodes} episodes), {total_movies} movies, {total_others} other videos", extra={"indent": 0})

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(f"""
        {Fore.CYAN}🎥 Video File Organizer 🎥{Style.RESET_ALL}
        Sort your video files into Movies, TV Shows, and Other Videos with ease!
        Move files from a source directory to a destination directory, with optional
        interactive renaming. 🚀
        """),
        formatter_class=CustomHelpFormatter,
        epilog=f"{Fore.MAGENTA}Example: python3 vorganize/main.py -s ~/videos -d ~/organized -i{Style.RESET_ALL}"
    )
    
    def valid_dir(path):
        if not os.path.isdir(path):
            raise argparse.ArgumentTypeError(f"{Fore.RED}Invalid directory: {path}{Style.RESET_ALL}")
        return path

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

    for arg in args_config:
        parser.add_argument(*arg['flags'], **{k: v for k, v in arg.items() if k != 'flags'})

    args = parser.parse_args()
    main(args.source, args.dest, args.interactive)