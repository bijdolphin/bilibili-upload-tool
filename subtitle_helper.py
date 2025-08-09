#!/usr/bin/env python3
"""
Helper script to download and burn Chinese subtitles into videos
"""

import subprocess
import os
from pathlib import Path
import json

def download_video_with_chinese_subtitles(youtube_url, output_filename):
    """
    Download video and Chinese subtitles, then burn subtitles into video
    """
    videos_dir = Path("videos")
    videos_dir.mkdir(exist_ok=True)
    
    base_path = videos_dir / output_filename
    video_path = videos_dir / f"{output_filename}.mp4"
    subtitle_path = videos_dir / f"{output_filename}.zh-Hans.srt"
    final_path = videos_dir / f"{output_filename}_final.mp4"
    
    ffmpeg_path = "/Users/fyj/workspace/video-automation-projects/social-auto-upload/ffmpeg"
    
    print(f"Step 1: Downloading video from {youtube_url}")
    
    # First, download the video without subtitles
    video_cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",
        "-o", str(video_path),
        "--no-playlist",
        youtube_url
    ]
    
    result = subprocess.run(video_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error downloading video: {result.stderr}")
        return None
    
    print(f"Step 2: Downloading Chinese subtitles")
    
    # Download Chinese subtitles separately
    # Try multiple subtitle options in order of preference
    subtitle_langs = ["zh-Hans", "zh-Hans-en", "zh-CN", "zh"]
    subtitle_downloaded = False
    
    for lang in subtitle_langs:
        print(f"Trying subtitle language: {lang}")
        subtitle_cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", lang,
            "--sub-format", "srt",
            "-o", f"{base_path}.%(ext)s",  # Fixed: Add extension placeholder
            youtube_url
        ]
        
        result = subprocess.run(subtitle_cmd, capture_output=True, text=True)
        print(f"Subtitle download output: {result.stdout}")
        
        # Check if subtitle file was created - fixed pattern
        possible_subtitle_files = list(videos_dir.glob(f"{output_filename}.{lang}.srt"))
        if not possible_subtitle_files:
            # Try alternate naming pattern
            possible_subtitle_files = list(videos_dir.glob(f"{output_filename}.*.srt"))
        
        if possible_subtitle_files:
            subtitle_path = possible_subtitle_files[0]
            subtitle_downloaded = True
            print(f"Subtitle downloaded: {subtitle_path}")
            break
    
    if not subtitle_downloaded:
        print("Warning: No Chinese subtitles found, returning video without subtitles")
        return str(video_path)
    
    print(f"Step 3: Burning subtitles into video using ffmpeg")
    
    # Burn subtitles into video using ffmpeg
    # Use subtitles filter to hard-code subtitles into video frames
    # Fix: Escape the subtitle path for ffmpeg
    subtitle_path_escaped = str(subtitle_path).replace(':', '\\:').replace('\\', '\\\\')
    burn_cmd = [
        ffmpeg_path,
        "-i", str(video_path),
        "-vf", f"subtitles={subtitle_path_escaped}:force_style='Fontsize=24,PrimaryColour=&H00FFFF&'",
        "-c:a", "copy",
        "-y",  # Overwrite output file
        str(final_path)
    ]
    
    print(f"Running ffmpeg command: {' '.join(burn_cmd)}")
    
    result = subprocess.run(burn_cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Success! Video with burned subtitles saved to: {final_path}")
        # Delete original video and rename final to original name
        os.remove(video_path)
        os.rename(final_path, video_path)
        # Clean up subtitle file
        if subtitle_path.exists():
            os.remove(subtitle_path)
        return str(video_path)
    else:
        print(f"Error burning subtitles: {result.stderr}")
        return str(video_path)

if __name__ == "__main__":
    # Test the function
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    result = download_video_with_chinese_subtitles(test_url, "test_video")
    if result:
        print(f"Final video: {result}")