#!/usr/bin/env python3
import subprocess
import os
import re
from pathlib import Path
import json
from typing import List, Tuple, Dict
import argparse
import sys

def find_video_and_srt(directory: str) -> Tuple[str, str]:
    """Find MP4 and SRT files in the given directory."""
    dir_path = Path(directory)
    if not dir_path.exists():
        raise ValueError(f"Directory {directory} does not exist")
    
    mp4_files = list(dir_path.glob("*.mp4"))
    srt_files = list(dir_path.glob("*.srt"))
    
    if not mp4_files:
        raise ValueError(f"No MP4 files found in {directory}")
    if not srt_files:
        raise ValueError(f"No SRT files found in {directory}")
    
    if len(mp4_files) > 1:
        print(f"Multiple MP4 files found, using: {mp4_files[0].name}")
    if len(srt_files) > 1:
        print(f"Multiple SRT files found, using: {srt_files[0].name}")
    
    return str(mp4_files[0]), str(srt_files[0])

def parse_srt(srt_file: str) -> List[Dict[str, any]]:
    """Parse SRT file and extract timestamps with text."""
    with open(srt_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to get subtitle blocks
    blocks = content.strip().split('\n\n')
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Extract subtitle number
            try:
                num = int(lines[0])
            except:
                continue
                
            # Extract timestamp
            timestamp_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', lines[1])
            if timestamp_match:
                start_time = timestamp_match.group(1).replace(',', '.')
                end_time = timestamp_match.group(2).replace(',', '.')
                
                # Join remaining lines as text
                text = ' '.join(lines[2:]).strip()
                
                subtitles.append({
                    'number': num,
                    'start': start_time,
                    'end': end_time,
                    'text': text,
                    'start_seconds': timestamp_to_seconds(start_time)
                })
    
    return subtitles

def timestamp_to_seconds(timestamp: str) -> float:
    """Convert timestamp to seconds."""
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds

def extract_frame(video_file: str, timestamp: str, output_file: str):
    """Extract a single frame from video at specified timestamp."""
    cmd = [
        'ffmpeg',
        '-ss', timestamp,
        '-i', video_file,
        '-frames:v', '1',
        '-q:v', '2',
        output_file,
        '-y'
    ]
    subprocess.run(cmd, capture_output=True, text=True)

def get_key_frames(subtitles: List[Dict], interval: float = 5.0) -> List[Dict]:
    """Select key frames based on meaningful content and time intervals."""
    key_frames = []
    last_time = -interval
    
    # Group subtitles that form complete sentences
    grouped_subtitles = []
    current_group = []
    
    for i, sub in enumerate(subtitles):
        current_group.append(sub)
        
        # Check if this subtitle ends a meaningful segment
        text = sub['text'].strip()
        if (text.endswith('.') or 
            text.endswith('?') or 
            text.endswith('!') or
            i == len(subtitles) - 1 or
            (i < len(subtitles) - 1 and subtitles[i+1]['start_seconds'] - sub['start_seconds'] > 2.0)):
            
            # Combine the group
            if current_group:
                combined_text = ' '.join([s['text'] for s in current_group])
                # Use the start of the first subtitle in the group
                grouped_subtitles.append({
                    'start': current_group[0]['start'],
                    'start_seconds': current_group[0]['start_seconds'],
                    'end': current_group[-1]['end'],
                    'text': combined_text.strip()
                })
                current_group = []
    
    # Select key frames from grouped subtitles
    for group in grouped_subtitles:
        # Skip if too close to last key frame (unless it's important content)
        if group['start_seconds'] - last_time >= interval or len(group['text']) > 50:
            key_frames.append(group)
            last_time = group['start_seconds']
    
    return key_frames

def main():
    parser = argparse.ArgumentParser(description='Extract frames from video based on transcript')
    parser.add_argument('directory', help='Directory containing MP4 and SRT files')
    parser.add_argument('--interval', type=float, default=5.0, 
                       help='Minimum interval between frames in seconds (default: 5.0)')
    args = parser.parse_args()
    
    try:
        # Find video and SRT files
        print(f"Looking for video and SRT files in: {args.directory}")
        video_file, srt_file = find_video_and_srt(args.directory)
        print(f"Found video: {Path(video_file).name}")
        print(f"Found SRT: {Path(srt_file).name}")
        
        # Create output directory
        output_dir = os.path.join(args.directory, "frames")
        Path(output_dir).mkdir(exist_ok=True)
        
        print("\nParsing SRT file...")
        subtitles = parse_srt(srt_file)
        print(f"Found {len(subtitles)} subtitle entries")
        
        print("\nSelecting key frames...")
        key_frames = get_key_frames(subtitles, interval=args.interval)
        print(f"Selected {len(key_frames)} key frames")
        
        print("\nExtracting frames...")
        frame_data = []
        
        for i, frame in enumerate(key_frames):
            timestamp = frame['start']
            output_file = os.path.join(output_dir, f"frame_{i:04d}.jpg")
            
            print(f"Extracting frame {i+1}/{len(key_frames)} at {timestamp}")
            extract_frame(video_file, timestamp, output_file)
            
            # Just use the filename since everything is in the frames directory
            filename = os.path.basename(output_file)
            
            frame_data.append({
                'frame_number': i,
                'timestamp': timestamp,
                'timestamp_seconds': frame['start_seconds'],
                'text': frame['text'],
                'image_path': filename
            })
        
        # Save frame data as JSON in the frames directory
        frame_data_path = os.path.join(output_dir, 'frame_data.json')
        with open(frame_data_path, 'w') as f:
            json.dump(frame_data, f, indent=2)
        
        # Also save all subtitles for full transcript
        all_subtitles_path = os.path.join(output_dir, 'all_subtitles.json')
        with open(all_subtitles_path, 'w') as f:
            json.dump(subtitles, f, indent=2)
        
        print(f"\nExtracted {len(key_frames)} frames to '{output_dir}' directory")
        print(f"Frame data saved to '{frame_data_path}'")
        print(f"Full transcript saved to '{all_subtitles_path}'")
        
        # Print summary
        print("\nFrame Summary:")
        print("-" * 80)
        for frame in frame_data[:10]:  # Show first 10
            print(f"[{frame['timestamp']}] {frame['text'][:60]}...")
        if len(frame_data) > 10:
            print(f"... and {len(frame_data) - 10} more frames")
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()