#!/usr/bin/env python3
import json
import os
from pathlib import Path
from datetime import datetime

def timestamp_to_seconds(timestamp):
    """Convert timestamp to seconds."""
    parts = timestamp.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2].replace(',', '.'))
    return hours * 3600 + minutes * 60 + seconds

def create_html_summary():
    """Create an HTML page that displays frames aligned with full transcript text."""
    
    # Load frame data and all subtitles
    with open('frame_data.json', 'r') as f:
        frames = json.load(f)
    
    with open('all_subtitles.json', 'r') as f:
        all_subtitles = json.load(f)
    
    # Create a mapping of frame timestamps to frame data
    frame_map = {frame['timestamp_seconds']: frame for frame in frames}
    frame_times = sorted(frame_map.keys())
    
    # Create HTML content
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Building TinyDocs - Visual Transcript</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 40px;
        }
        .summary-section {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 40px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .key-topics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .topic-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #0066cc;
        }
        .topic-timestamp {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .transcript-section {
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .frame-marker {
            margin: 30px 0;
            padding: 20px;
            background: #f0f7ff;
            border-radius: 8px;
            border: 1px solid #d0e5ff;
        }
        .frame-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            gap: 15px;
        }
        .timestamp {
            font-weight: bold;
            color: #0066cc;
            font-family: monospace;
            font-size: 14px;
        }
        .frame-number {
            background: #0066cc;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .frame-image {
            margin: 15px 0;
        }
        .frame-image img {
            max-width: 480px;
            height: auto;
            border-radius: 4px;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .frame-image img:hover {
            transform: scale(1.02);
        }
        .transcript-text {
            font-size: 16px;
            color: #333;
            margin: 8px 0;
        }
        .transcript-text.highlight {
            background: #fffae6;
            padding: 2px 4px;
            border-radius: 3px;
        }
        .nav-buttons {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }
        .nav-button {
            background: #0066cc;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .nav-button:hover {
            background: #0052a3;
        }
        .toc {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 20px;
        }
        .toc h3 {
            margin-top: 0;
        }
        .toc-link {
            display: block;
            color: #0066cc;
            text-decoration: none;
            padding: 5px 0;
        }
        .toc-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Building TinyDocs - A Docs Site Micro SaaS</h1>
    
    <div class="summary-section">
        <h2>Video Summary</h2>
        <p>This video demonstrates building a documentation site application called "TinyDocs" as an alternative to Mintlify. The project aims to create a simpler, more affordable solution for managing and publishing documentation.</p>
        
        <h3>Key Topics Covered:</h3>
        <div class="key-topics">
            <div class="topic-card">
                <strong>Introduction to TinyDocs</strong>
                <div class="topic-timestamp">00:00:00 - 00:02:00</div>
            </div>
            <div class="topic-card">
                <strong>Mintlify Alternative</strong>
                <div class="topic-timestamp">00:00:40 - 00:01:40</div>
            </div>
            <div class="topic-card">
                <strong>Project Planning with Bear Cloud</strong>
                <div class="topic-timestamp">00:01:49 - 00:04:00</div>
            </div>
            <div class="topic-card">
                <strong>AI-Powered Documentation</strong>
                <div class="topic-timestamp">00:03:00 - 00:04:30</div>
            </div>
        </div>
        
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
                <span class="frame-number">Frame {frame['frame_number'] + 1}</span>
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
                <span class="frame-number">Frame {frame['frame_number'] + 1}</span>
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
    
    # Write HTML file
    with open('visual_transcript.html', 'w') as f:
        f.write(html_content)
    
    print("Created visual_transcript.html")

def create_markdown_summary():
    """Create a Markdown summary with full transcript and frame markers."""
    
    # Load frame data and all subtitles
    with open('frame_data.json', 'r') as f:
        frames = json.load(f)
    
    with open('all_subtitles.json', 'r') as f:
        all_subtitles = json.load(f)
    
    # Create a mapping of frame timestamps to frame data
    frame_map = {frame['timestamp_seconds']: frame for frame in frames}
    frame_times = sorted(frame_map.keys())
    
    md_content = """# Building TinyDocs - A Docs Site Micro SaaS

## Video Summary

This video demonstrates building a documentation site application called "TinyDocs" as an alternative to Mintlify. The project aims to create a simpler, more affordable solution for managing and publishing documentation.

## Key Topics

- **Introduction to TinyDocs** (00:00:00 - 00:02:00)
- **Mintlify Alternative** (00:00:40 - 00:01:40)
- **Project Planning with Bear Cloud** (00:01:49 - 00:04:00)
- **AI-Powered Documentation** (00:03:00 - 00:04:30)

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
            
            md_content += f"\n---\n\n### 🎬 Frame {frame['frame_number'] + 1} - [{frame['timestamp']}]\n\n"
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
    
    # Write markdown file
    with open('visual_transcript.md', 'w') as f:
        f.write(md_content)
    
    print("Created visual_transcript.md")

def create_api_ready_format():
    """Create a format ready for API consumption with full transcript."""
    
    # Load frame data and all subtitles
    with open('frame_data.json', 'r') as f:
        frames = json.load(f)
    
    with open('all_subtitles.json', 'r') as f:
        all_subtitles = json.load(f)
    
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
        "video_title": "Building TinyDocs - A Docs Site Micro SaaS",
        "total_duration": frames[-1]['timestamp'] if frames else "00:00:00",
        "frame_count": len(frames),
        "subtitle_count": len(all_subtitles),
        "segments": segments,
        "full_transcript": " ".join([s['text'] for s in all_subtitles])
    }
    
    # Save API-ready data
    with open('api_frame_data.json', 'w') as f:
        json.dump(api_data, f, indent=2)
    
    print(f"Created api_frame_data.json with {len(segments)} segments and full transcript")

if __name__ == "__main__":
    print("Creating visual summaries with full transcript...")
    
    # First run extract_frames.py to ensure we have all_subtitles.json
    import subprocess
    subprocess.run(['python', 'extract_frames.py'], capture_output=True)
    
    create_html_summary()
    create_markdown_summary()
    create_api_ready_format()
    print("\nDone! Created:")
    print("- visual_transcript.html (open in browser for interactive view with full transcript)")
    print("- visual_transcript.md (for documentation with full transcript)")
    print("- api_frame_data.json (for API consumption with segmented transcript)")