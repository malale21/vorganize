# Vorganize: Video File Organizer

Vorganize is a powerful Python script designed to organize your video files with ease. It sorts videos into structured directories for TV shows, movies, and other videos, handles subtitles, and offers an interactive mode for renaming and categorizing files. With a user-friendly command-line interface, colored logging, and progress bars, Vorganize makes video organization seamless and efficient.
Features

## Automatic Sorting:

## Organizes video files into:
TV Shows: Groups episodes by series and season (e.g., shows/Breaking Bad/Season 1/Breaking Bad S01E01.mkv).
Movies: Places movies in a dedicated folder (e.g., Movies/Inception (2010).mp4).
Other Videos: Stores miscellaneous videos in a separate directory (e.g., other_videos/RandomVideo.mp4).


## Recognizes common naming conventions (e.g., S01E01, Season 01 Episode 01, 1x01, Movie (2020)).


### Subtitle Handling:

Detects and moves subtitle files (.srt, .sub, .vtt, etc.) alongside their corresponding videos.
Renames subtitles to match renamed videos in interactive mode.


## Interactive Mode:

Allows manual renaming of video files and subtitles.
Prompts for categorization (movies, TV shows, or other) for files that don’t match automatic patterns.


## Progress Bars:

Displays progress bars using tqdm for:
Interactive file processing.
Moving TV show episodes and subtitles.




## Robust Error Handling:

Skips files that already exist in the destination to avoid overwrites.
Handles KeyboardInterrupt (Ctrl+C) gracefully, saving progress (JSON files and moved files).
Logs errors (e.g., missing files, failed moves) with detailed messages.


## JSON Metadata Storage:

Stores metadata in JSON files (shows.json, movies.json, other_videos.json) for tracking organized files.
Supports resuming by skipping already processed files.

```json
{
    "shows": [
        "Black Bird",
        "Desperate Housewives",
        "Extracurricular",
        "FOREVER 2025",
        "Freaks and Geeks",
        "Mercy For None",
        "Mr Robot",
        "Mr Robot - Season 4",
        "Severance",
        "Squid Game",
        "Squid Game - Season 3",
        "Weak Hero Class 1",
        "Weak Hero Class 1 - Season 2",
        "[KDL]"
    ]
}
```

### Colored Logging:

Uses colorama for colorful, indented console output:
Green for success/info.
Yellow for warnings (e.g., skipped files).
Red for errors (e.g., move failures).
Blue for debug messages (e.g., regex matches).




## Modular Design:

Organized as a Python package with modules for core utilities, file organization, storage, and interactive processing.
Easy to extend or integrate into other projects.



# Installation
## Prerequisites

Python: Version 3.6 or higher.
Operating System: Compatible with Linux, macOS, and Windows (tested on Linux).

## Steps
```bash
# Clone the Repository:
git clone https://github.com/malale21/vorganize.git

cd vorganize

pip install -r requirements.txt # or

sudo apt install python3-colorama python3-tqdm # If your'e on debian linux

# Add the main.py file to your path (optional)
sudo ln -sf ./main.py  /usr/sbin/vorganize
```

## Set Up JSON Storage Directory:Create a directory for JSON metadata files (default: /home/username/.local/movies_script/):
```bash
mkdir -p ~/.local/movies_script
```
## Update the script_dir parameter in main.py if you prefer a different location.

## Verify Directory Structure:Ensure the vorganize directory contains:
```bash
vorganize/
├── __init__.py
├── core.py
├── organize.py
├── storage.py
├── interactive.py
├── main.py
```


## Usage
## Run Vorganize from the command line to organize video files from a source directory to a destination directory.

## Command
```bash
python vorganize/main.py -s <source_dir> -d <dest_dir> [-i]


-s, --source: Source directory containing video files (required).
-d, --dest: Destination directory for organized files (required).
-i, --interactive: Enable interactive mode for renaming and categorizing files (optional).

Example
Organize videos in /home/user/videos into /home/user/organized with interactive mode:
python vorganize/main.py -s ~/videos -d ~/organized -i

Example Files
Input files in /home/user/videos:

Breaking Bad S01E01.mkv
Breaking Bad S01E01.srt
Inception (2010).mp4
RandomVideo.mp4

Output structure in /home/user/organized:

organized/
├── shows/
│   └── Breaking Bad/
│       └── Season 1/
│           ├── Breaking Bad S01E01.mkv
│           ├── Breaking Bad S01E01.srt
├── Movies/
│   └── Inception (2010).mp4
├── other_videos/
│   └── RandomVideo.mp4
```
## JSON files in ~/.local/movies_script/:
```json
{"shows": ["Breaking Bad"], "shows_subtitles": ["Breaking Bad S01E01.srt"]}
{"movies": ["Inception (2010).mp4"], "movies_subtitles": []}
{"videos": ["RandomVideo.mp4"], "videos_subtitles": []}
```
## Interactive Mode

## In interactive mode (-i), Vorganize prompts for:

```bash
Renaming each uncategorized video file (press Enter to keep the original name).
Categorizing as movie (m), TV show (s), or other (o).Example prompt:

Starting interactive mode
  Processing RandomVideo.mp4
Enter new name for 'RandomVideo.mp4' without extension (press Enter to keep): New Video
  Renamed video: RandomVideo.mp4 -> New Video.mp4
Categorize 'New Video.mp4' (m=movies, s=tv-shows, o=other): o
```
Sample Output

```bash
Scanning directory: /home/user/videos
    Extracted series 'Breaking Bad' with season 1 from 'Breaking Bad S01E01.mkv'
    Subtitle found: Breaking Bad S01E01.mkv -> Breaking Bad S01E01.srt
Processing Breaking Bad
Moving Breaking Bad: 100%|██████████| 1/1 [00:00<00:00, 10.00file/s]
  Season 1: Moved 1 episodes, 1 subtitles to Breaking Bad/Season 1
Completed Breaking Bad: 1 episodes, 1 subtitles, 0 skipped, 0 errors across 1 seasons
Processing movies
  Moved 1 movies, 0 subtitles to Movies
Starting interactive mode
Interactive processing:   0%|          | 0/1 [00:00<?, ?file/s]
  Processing RandomVideo.mp4
Enter new name for 'RandomVideo.mp4' without extension (press Enter to keep): 
Categorize 'RandomVideo.mp4' (m=movies, s=tv-shows, o=other): o
Interactive processing: 100%|██████████| 1/1 [00:05<00:00,  5.00s/file]
Moving files
Processing videos
  Moved 1 videos, 0 subtitles to other_videos
Interactive mode complete: 0 series (0 episodes), 0 movies, 1 other videos
Summary: Processed 1 series (1 episodes), 1 movies, 1 other videos
```
## Configuration
```yaml
Video Extensions: Supports .mp4, .avi, .mkv, .mov, .wmv (edit video_ext in main.py to add more).
Subtitle Extensions: Supports .srt, .sub, .idx, .ssa, .ass, .vtt, .smi, .sami, .stl (edit common_subtitle_exts in main.py).
Series Pattern: Recognizes formats like S01E01, s1e1, Season 01 Episode 01, 1x01 (edit series_pattern in main.py).
Movie Patterns: Matches filenames with years (e.g., Movie (2020).mp4) or specific formats (edit movie_pattern, movie_pattern2, movie_pattern3 in main.py).
JSON Directory: Default is ~/.local/movies_script/ (edit script_dir in main.py).
```
## Handling Interruptions

Press Ctrl+C during interactive mode or file moving to exit gracefully.
Progress is saved:

JSON files are updated for each processed file.
Moved files remain in their destination directories.


## Rerun the script to continue processing; existing files are skipped to avoid duplicates.

## Debugging

Enable debug logs by setting logger.setLevel(logging.DEBUG) in main.py to see detailed regex matching and file processing information (blue text).
Check logs for warnings (yellow) or errors (red) to diagnose issues with specific files.

## Contributing
Contributions are welcome! To contribute:

## Fork the repository.
Create a new branch: git checkout -b feature/your-feature.
Make changes and commit: git commit -m "Add your feature".
Push to your fork: git push origin feature/your-feature.
Open a pull request.

Please include tests and update the README if adding new features.
License
This project is licensed under the MIT License. See the LICENSE file for details.
## Contact
For issues or feature requests, open an issue on the GitHub repository or contact @malale21 .

## Happy organizing! 🎥🚀