#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime
import argparse
import subprocess
import sys

def timestamp_to_seconds(timestamp):
    """Convert timestamp to seconds."""
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2].replace(',', '.'))
    return hours * 3600 + minutes * 60 + seconds

def check_and_extract_frames(directory):
    """Check if frames exist, if not run extract_frames.py."""
    frames_dir = os.path.join(directory, "frames")
    frame_data_path = os.path.join(frames_dir, "frame_data.json")
    
    if not os.path.exists(frame_data_path):
        print(f"Frame data not found. Running extract_frames.py...")
        try:
            # Run extract_frames.py with the directory
            cmd = [sys.executable, "extract_frames.py", directory]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error running extract_frames.py:")
                print(result.stderr)
                sys.exit(1)
            print("Frame extraction completed.")
        except Exception as e:
            print(f"Error running extract_frames.py: {e}")
            sys.exit(1)
    else:
        print(f"Frame data found at {frame_data_path}")

def create_html_summary(directory):
    """Create an HTML page that displays frames aligned with full transcript text."""
    frames_dir = os.path.join(directory, "frames")
    
    # Load frame data and all subtitles
    with open(os.path.join(frames_dir, 'frame_data.json'), 'r') as f:
        frames = json.load(f)
    
    with open(os.path.join(frames_dir, 'all_subtitles.json'), 'r') as f:
        all_subtitles = json.load(f)
    
    # Create a mapping of frame timestamps to frame data
    frame_map = {frame['timestamp_seconds']: frame for frame in frames}
    frame_times = sorted(frame_map.keys())
    
    # Get video title from directory name
    video_title = Path(directory).name.replace('-', ' ').title()
    
    # Create HTML content
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{video_title} - Visual Transcript</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 40px;
        }}
        .summary-section {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .key-topics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .topic-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #0066cc;
        }}
        .topic-timestamp {{
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }}
        .transcript-section {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .frame-marker {{
            margin: 30px 0;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 8px;
            border: 1px solid #d0e5ff;
        }}
        .frame-header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            gap: 15px;
        }}
        .timestamp {{
            font-weight: bold;
            color: #0066cc;
            font-family: monospace;
            font-size: 14px;
        }}
        .frame-number {{
            background: #0066cc;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }}
        .frame-image {{
            margin: 15px 0;
        }}
        .frame-image img {{
            max-width: 480px;
            height: auto;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        .frame-image img:hover {{
            transform: scale(1.02);
        }}
        .transcript-text {{
            font-size: 16px;
            color: #333;
            margin: 8px 0;
        }}
        .transcript-text.highlight {{
            background: #fffae6;
            padding: 2px 4px;
            border-radius: 3px;
        }}
        .nav-buttons {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }}
        .nav-button {{
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        .nav-button:hover {{
            background: #0052a3;
        }}
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .toc h3 {{
            margin-top: 0;
        }}
        .toc-link {{
            display: block;
            color: #0066cc;
            text-decoration: none;
            padding: 5px 0;
        }}
        .toc-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{video_title}</h1>
    
    <div class="summary-section">
        <h2>Video Summary</h2>
        <p>This video transcript has been processed with visual markers at key moments.</p>
        
        <div class="toc">
            <h3>Quick Navigation</h3>
"""
    
    # Add table of contents
    for i, frame in enumerate(frames[::10]):  # Every 10th frame
        html_content += f'            <a href="#frame-{frame["frame_number"]}" class="toc-link">[{frame["timestamp"]}] {frame["text"][:50]}...</a>\n'
    
    html_content += """
        </div>
    </div>
    
    <div class="transcript-section">
        <h2>Full Transcript with Visual Markers</h2>
"""
    
    # Process all subtitles and insert frame markers
    current_frame_idx = 0
    
    for subtitle in all_subtitles:
        sub_time = subtitle['start_seconds']
        
        # Check if we should insert a frame marker
        while current_frame_idx < len(frame_times) and frame_times[current_frame_idx] <= sub_time:
            frame_time = frame_times[current_frame_idx]
            frame = frame_map[frame_time]
            
            html_content += f"""
        <div class="frame-marker" id="frame-{frame['frame_number']}">
            <div class="frame-header">
                <span class="timestamp">{frame['timestamp']}</span>
                <span class="frame-number">Frame {frame['frame_number']}</span>
            </div>
            <div class="frame-image">
                <img src="{frame['image_path']}" alt="Frame at {frame['timestamp']}" loading="lazy">
            </div>
        </div>
"""
            current_frame_idx += 1
        
        # Add the transcript text
        highlight_class = ""
        # Highlight text that appears in a frame
        for frame_time in frame_times:
            if abs(sub_time - frame_time) < 1.0:
                highlight_class = " highlight"
                break
        
        html_content += f'        <p class="transcript-text{highlight_class}"><span class="timestamp">[{subtitle["start"]}]</span> {subtitle["text"]}</p>\n'
    
    # Add any remaining frames
    while current_frame_idx < len(frame_times):
        frame_time = frame_times[current_frame_idx]
        frame = frame_map[frame_time]
        
        html_content += f"""
        <div class="frame-marker" id="frame-{frame['frame_number']}">
            <div class="frame-header">
                <span class="timestamp">{frame['timestamp']}</span>
                <span class="frame-number">Frame {frame['frame_number']}</span>
            </div>
            <div class="frame-image">
                <img src="{frame['image_path']}" alt="Frame at {frame['timestamp']}" loading="lazy">
            </div>
        </div>
"""
        current_frame_idx += 1
    
    # Add closing tags
    html_content += """
    </div>
    
    <div class="nav-buttons">
        <button class="nav-button" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">Top</button>
    </div>
    
    <script>
        // Add click handlers to images for full-screen view
        document.querySelectorAll('.frame-image img').forEach(img => {
            img.onclick = function() {
                window.open(this.src, '_blank');
            };
        });
        
        // Smooth scroll for TOC links
        document.querySelectorAll('.toc-link').forEach(link => {
            link.onclick = function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            };
        });
    </script>
</body>
</html>
"""
    
    # Write HTML file to frames directory
    output_path = os.path.join(frames_dir, 'visual_transcript.html')
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"Created {output_path}")

def create_markdown_summary(directory):
    """Create a Markdown summary with full transcript and frame markers."""
    frames_dir = os.path.join(directory, "frames")
    
    # Load frame data and all subtitles
    with open(os.path.join(frames_dir, 'frame_data.json'), 'r') as f:
        frames = json.load(f)
    
    with open(os.path.join(frames_dir, 'all_subtitles.json'), 'r') as f:
        all_subtitles = json.load(f)
    
    # Create a mapping of frame timestamps to frame data
    frame_map = {frame['timestamp_seconds']: frame for frame in frames}
    frame_times = sorted(frame_map.keys())
    
    # Get video title from directory name
    video_title = Path(directory).name.replace('-', ' ').title()
    
    md_content = f"""# {video_title}

## Video Summary

This video transcript has been processed with visual markers at key moments.

## Full Transcript with Visual Markers

"""
    
    # Process all subtitles and insert frame markers
    current_frame_idx = 0
    
    for subtitle in all_subtitles:
        sub_time = subtitle['start_seconds']
        
        # Check if we should insert a frame marker
        while current_frame_idx < len(frame_times) and frame_times[current_frame_idx] <= sub_time:
            frame_time = frame_times[current_frame_idx]
            frame = frame_map[frame_time]
            
            md_content += f"\n---\n\n### 🎬 Frame {frame['frame_number']} - [{frame['timestamp']}]\n\n"
            md_content += f"![Frame at {frame['timestamp']}]({frame['image_path']})\n\n"
            md_content += f"---\n\n"
            
            current_frame_idx += 1
        
        # Add the transcript text
        md_content += f"**[{subtitle['start']}]** {subtitle['text']}\n\n"
    
    # Add any remaining frames
    while current_frame_idx < len(frame_times):
        frame_time = frame_times[current_frame_idx]
        frame = frame_map[frame_time]
        
        md_content += f"\n---\n\n### 🎬 Frame {frame['frame_number'] + 1} - [{frame['timestamp']}]\n\n"
        md_content += f"![Frame at {frame['timestamp']}]({frame['image_path']})\n\n"
        md_content += f"---\n\n"
        
        current_frame_idx += 1
    
    # Write markdown file to frames directory
    output_path = os.path.join(frames_dir, 'visual_transcript.md')
    with open(output_path, 'w') as f:
        f.write(md_content)
    
    print(f"Created {output_path}")

def create_api_ready_format(directory):
    """Create a format ready for API consumption with full transcript."""
    frames_dir = os.path.join(directory, "frames")
    
    # Load frame data and all subtitles
    with open(os.path.join(frames_dir, 'frame_data.json'), 'r') as f:
        frames = json.load(f)
    
    with open(os.path.join(frames_dir, 'all_subtitles.json'), 'r') as f:
        all_subtitles = json.load(f)
    
    # Get video title from directory name
    video_title = Path(directory).name.replace('-', ' ').title()
    
    # Group subtitles between frames
    frame_times = sorted([f['timestamp_seconds'] for f in frames])
    
    # Create segments between frames
    segments = []
    current_segment = []
    current_frame_idx = 0
    
    for subtitle in all_subtitles:
        sub_time = subtitle['start_seconds']
        
        # Check if we've passed a frame boundary
        if current_frame_idx < len(frame_times) and sub_time >= frame_times[current_frame_idx]:
            # Save current segment if it has content
            if current_segment:
                # Find the corresponding frame
                frame = None
                for f in frames:
                    if f['timestamp_seconds'] == frame_times[current_frame_idx - 1]:
                        frame = f
                        break
                
                if frame:
                    segments.append({
                        "frame_number": frame['frame_number'],
                        "timestamp": frame['timestamp'],
                        "timestamp_seconds": frame['timestamp_seconds'],
                        "image_path": frame['image_path'],
                        "transcript_segment": " ".join([s['text'] for s in current_segment])
                    })
            
            current_segment = []
            current_frame_idx += 1
        
        current_segment.append(subtitle)
    
    # Don't forget the last segment
    if current_segment and current_frame_idx > 0:
        frame = None
        for f in frames:
            if f['timestamp_seconds'] == frame_times[current_frame_idx - 1]:
                frame = f
                break
        
        if frame:
            segments.append({
                "frame_number": frame['frame_number'],
                "timestamp": frame['timestamp'],
                "timestamp_seconds": frame['timestamp_seconds'],
                "image_path": frame['image_path'],
                "transcript_segment": " ".join([s['text'] for s in current_segment])
            })
    
    # Create API-ready structure
    api_data = {
        "video_title": video_title,
        "total_duration": frames[-1]['timestamp'] if frames else "00:00:00",
        "frame_count": len(frames),
        "subtitle_count": len(all_subtitles),
        "segments": segments,
        "full_transcript": " ".join([s['text'] for s in all_subtitles])
    }
    
    # Save API-ready data to frames directory
    output_path = os.path.join(frames_dir, 'api_frame_data.json')
    with open(output_path, 'w') as f:
        json.dump(api_data, f, indent=2)
    
    print(f"Created {output_path} with {len(segments)} segments and full transcript")

def main():
    parser = argparse.ArgumentParser(description='Create visual summaries from extracted frames and transcript')
    parser.add_argument('directory', help='Directory containing frames (or MP4/SRT if frames not yet extracted)')
    args = parser.parse_args()
    
    try:
        # Check if frames exist, extract if needed
        check_and_extract_frames(args.directory)
        
        print(f"\nCreating visual summaries for: {args.directory}")
        
        # Create all output formats
        create_html_summary(args.directory)
        create_markdown_summary(args.directory)
        create_api_ready_format(args.directory)
        
        frames_dir = os.path.join(args.directory, "frames")
        print(f"\nDone! Created in {frames_dir}:")
        print("- visual_transcript.html (open in browser for interactive view)")
        print("- visual_transcript.md (for documentation)")
        print("- api_frame_data.json (for API consumption)")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()