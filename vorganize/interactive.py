from pathlib import Path
import os, sys
import logging
from colorama import Fore, Style
from collections import defaultdict
from .core import extract_series_title, find_subtitle
from .storage import store_as_json
from .organize import move_series, move_items
from .core import find_subtitle
from tqdm import tqdm

"""_summary_:
Interactive video file organizer.
This module provides functionality to interactively rename and categorize video files into Movies, TV Shows, and Other Videos.
It allows users to rename files, categorize them, and move them to appropriate directories. 
"""


logger = logging.getLogger(__name__)

def handle_inter(source, videos, dest_dict, series_pattern, common_subtitle_exts):
    """Handle interactive renaming and categorization of videos with a progress bar."""
    user_series_dict = defaultdict(lambda: defaultdict(list))
    user_movie_list = []
    user_vid_list = []
    
    logger.info("Starting interactive mode", extra={"indent": 0})
    try:
        # Wrap the loop with tqdm for progress bar
        for video_file, subtitle_file in tqdm(videos, desc="Interactive processing", unit="file",bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]"):
            logger.info(f"Processing {video_file}", extra={"indent": 2})
            original_video_file = video_file
            
            # Prompt for renaming video file
            try:
                new_name = input(f"{Fore.CYAN}Enter new name for '{video_file}' without extension (press Enter to keep): {Style.RESET_ALL}")
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt detected during renaming. Saving progress and exiting.", extra={"indent": 2})
                break

            if new_name:
                new_ext = f'.{video_file.split(".")[-1]}'
                new_video_file = new_name + new_ext
                try:
                    os.rename(source / video_file, source / new_video_file)
                    logger.info(f"Renamed video: {video_file} -> {new_video_file}", extra={"indent": 4})
                    video_file = new_video_file
                except OSError as e:
                    logger.error(f"Failed to rename video {video_file}: {e}", extra={"indent": 4})
                    continue

            # Rename subtitle file if it exists and video was renamed
            if subtitle_file and new_name:
                new_sub_ext = f'.{subtitle_file.split(".")[-1]}'
                new_subtitle_file = new_name + new_sub_ext
                try:
                    os.rename(source / subtitle_file, source / new_subtitle_file)
                    logger.info(f"Renamed subtitle: {subtitle_file} -> {new_subtitle_file}", extra={"indent": 4})
                    subtitle_file = new_subtitle_file
                except OSError as e:
                    logger.error(f"Failed to rename subtitle {subtitle_file}: {e}", extra={"indent": 4})
                    subtitle_file = None

            # Prompt for categorization
            try:
                while True:
                    category = input(f"{Fore.CYAN}Categorize '{video_file}' (m=movies, s=tv-shows, o=other): {Style.RESET_ALL}").lower()
                    if category in dest_dict:
                        break
                    logger.error(f"Invalid category '{category}'. Please enter m, s, or o.", extra={"indent": 4})
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt detected during categorization. Saving progress and exiting.", extra={"indent": 2})
                break

            # Store in appropriate data structure
            if category == "s":
                series_title, season_number = extract_series_title(video_file, series_pattern)
                if series_title:
                    series_title = series_title.replace('.', ' ')
                    user_series_dict[series_title][season_number].append((video_file, subtitle_file))
                    store_as_json("s", (series_title, season_number, video_file), dest_dict["s"].parent / "shows.json")
                else:
                    logger.warning(f"Could not extract series title from {video_file}. Skipping.", extra={"indent": 4})
            elif category == "m":
                user_movie_list.append((video_file, subtitle_file))
                store_as_json("m", video_file, dest_dict["m"].parent / "movies.json")
            else:
                user_vid_list.append((video_file, subtitle_file))
                store_as_json("o", video_file, dest_dict["o"].parent / "other_videos.json")

    except KeyboardInterrupt:
        logger.warning("Keyboard interrupt detected. Saving progress and exiting.", extra={"indent": 0})

    # Move files processed so far
    if user_series_dict or user_movie_list or user_vid_list:
        logger.info("Moving files processed before interrupt", extra={"indent": 0})
        move_series(user_series_dict, source, dest_dict["s"])
        move_items(user_movie_list, source, dest_dict["m"], item_type="movies")
        move_items(user_vid_list, source, dest_dict["o"], item_type="videos")

    # Log summary
    total_series = len(user_series_dict)
    total_episodes = sum(len(episodes) for series in user_series_dict.values() for episodes in series.values())
    total_movies = len(user_movie_list)
    total_others = len(user_vid_list)
    logger.info(f"Interactive mode interrupted: Processed {total_series} series ({total_episodes} episodes), {total_movies} movies, {total_others} other videos", extra={"indent": 0})
    
    if total_series or total_movies or total_others:
        logger.info("Progress saved. Run the script again to continue processing.", extra={"indent": 0})
    sys.exit(0)