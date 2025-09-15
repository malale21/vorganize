from pathlib import Path
import shutil
import sys, time
import logging
from tqdm import tqdm
from .core import find_subtitle, extract_series_title
from .storage import store_as_json

logger = logging.getLogger(__name__)

def prepare_lists(filename, path, series_dict, movies, other_videos, series_pattern, movie_pattern, movie_pattern2, movie_pattern3, common_subtitle_exts, shows_json, movies_json, other_videos_json):
    """Sort video files into series, movies, or other videos, with subtitles."""
    subtitle_file = find_subtitle(filename, path, common_subtitle_exts)
    if subtitle_file:
        logger.info(f"Subtitle found: {filename} -> {subtitle_file}", extra={"indent": 2})

    if series_pattern.search(filename):
        series_title, season_number = extract_series_title(filename, series_pattern)
        if series_title:
            print(season_number)
            series_title = series_title.replace('.', ' ')
            series_dict[series_title][season_number].append((filename, subtitle_file))
            store_as_json("s", (series_title, season_number, filename), shows_json)
    elif any(pat.search(filename) for pat in [movie_pattern, movie_pattern2, movie_pattern3]):
        movies.append((filename, subtitle_file))
        store_as_json("m", filename, movies_json)
    else:
        other_videos.append((filename, subtitle_file))
        store_as_json("o", filename, other_videos_json)

def move_series(series_dict, path, dest_dir):
    """Move series episodes and subtitles to destination directories with a progress bar."""
    try:
        for series_title, seasons in series_dict.items():
            if not seasons or all(len(episodes) == 0 for episodes in seasons.values()):
                logger.warning(f"Skipping {series_title}: No episodes.", extra={"indent": 0})
                continue

            logger.info(f"Processing {series_title}", extra={"indent": 0})
            series_dir = Path(dest_dir) / series_title
            series_dir.mkdir(parents=True, exist_ok=True)

            total_episodes, total_subtitles, skipped, errors = 0, 0, 0, 0
            # Calculate total episodes for progress bar
            total_files = sum(len(episodes) for episodes in seasons.values())
            progress_bar = tqdm(total=total_files, desc=f"Moving {series_title}", unit="file",bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]")

            for season_number, episodes in sorted(seasons.items()):
                if not episodes:
                    logger.warning(f"Skipping Season {season_number}: No episodes.", extra={"indent": 2})
                    progress_bar.update(0)  # No files to process, no update needed
                    continue

                season_dir = series_dir / f"Season {season_number}"
                season_dir.mkdir(exist_ok=True)
                season_path = f"{series_title}/Season {season_number}"

                moved_episodes, moved_subtitles = [], []
                for video_file, subtitle_file in episodes:
                    # Move video file
                    source = path / video_file
                    dest = season_dir / video_file
                    try:
                        if dest.exists():
                            skipped += 1
                        elif not source.exists():
                            errors += 1
                            logger.error(f"\nVideo missing: {video_file}", extra={"indent": 4})
                        else:
                            shutil.move(source, dest)
                            moved_episodes.append(video_file)
                            time.sleep(0.5)
                            total_episodes += 1
                    except (OSError, shutil.Error) as e:
                        errors += 1
                        logger.error(f"\nVideo move failed: {video_file} ({e})", extra={"indent": 4})

                    # Move subtitle file if it exists
                    if subtitle_file:
                        source_sub = path / subtitle_file
                        dest_sub = season_dir / subtitle_file
                        try:
                            if dest_sub.exists():
                                skipped += 1
                            elif not source_sub.exists():
                                errors += 1
                                logger.error(f"\nSubtitle missing: {subtitle_file}", extra={"indent": 4})
                            else:
                                shutil.move(source_sub, dest_sub)
                                moved_subtitles.append(subtitle_file)
                                total_subtitles += 1
                        except (OSError, shutil.Error) as e:
                            errors += 1
                            logger.error(f"\nSubtitle move failed: {subtitle_file} ({e})", extra={"indent": 4})

                    progress_bar.update(1)  # Update progress after processing each episode

                if moved_episodes or moved_subtitles:
                    logger.info(f"\nSeason {season_number}: Moved {len(moved_episodes)} episodes, {len(moved_subtitles)} subtitles to {season_path}", extra={"indent": 2})
                if skipped > 0:
                    logger.warning(f"\nSeason {season_number}: Skipped {skipped} files (already exist)", extra={"indent": 2})

            progress_bar.close()
            logger.info(f"\nCompleted {series_title}: {total_episodes} episodes, {total_subtitles} subtitles, {skipped} skipped, {errors} errors across {len([s for s in seasons if seasons[s]])} seasons", extra={"indent": 0})

    except KeyboardInterrupt:
        logger.warning(f"\nKeyboard interrupt detected while moving series '{series_title}'. Saving progress and exiting.", extra={"indent": 0})
        progress_bar.close()
        sys.exit(0)

def move_items(items, path, dest_dir, item_type="videos"):
    """Move items (movies or other videos) and subtitles to destination directory."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir.name
    logger.info(f"Processing {item_type}", extra={"indent": 0})

    moved_items, moved_subtitles, skipped, errors = [], [], 0, 0
    for item, subtitle_file in items:
        source = path / item
        dest = dest_dir / item
        try:
            if dest.exists():
                skipped += 1
            elif not source.exists():
                errors += 1
                logger.error(f"{item_type[:-1]} missing: {item}", extra={"indent": 2})
            else:
                shutil.move(source, dest)
                moved_items.append(item)
        except (OSError, shutil.Error) as e:
            errors += 1
            logger.error(f"{item_type[:-1]} move failed: {item} ({e})", extra={"indent": 2})

        if subtitle_file:
            source_sub = path / subtitle_file
            dest_sub = dest_dir / subtitle_file
            try:
                if dest_sub.exists():
                    skipped += 1
                elif not source_sub.exists():
                    errors += 1
                    logger.error(f"Subtitle missing: {subtitle_file}", extra={"indent": 2})
                else:
                    shutil.move(source_sub, dest_sub)
                    moved_subtitles.append(subtitle_file)
            except (OSError, shutil.Error) as e:
                errors += 1
                logger.error(f"Subtitle move failed: {subtitle_file} ({e})", extra={"indent": 2})

    if moved_items or moved_subtitles:
        logger.info(f"Moved {len(moved_items)} {item_type}, {len(moved_subtitles)} subtitles to {dest_path}", extra={"indent": 0})
    if skipped > 0:
        logger.warning(f"Skipped {skipped} {item_type} (already exist)", extra={"indent": 0})
    if errors > 0:
        logger.error(f"Encountered {errors} errors", extra={"indent": 0})