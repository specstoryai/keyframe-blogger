[![Prompt Stats](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fstats.specstory.com%2Fanalyze%3Frepo%3Dspecstoryai%2Fkeyframe-blogger&query=%24.data.promptCount&label=%23%20Prompts&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI1NTAiIGhlaWdodD0iNTUwIiBmaWxsPSJub25lIj48cGF0aCBmaWxsPSIjNTJCN0Q2IiBkPSJtMTE1LjQ0MyA1NDkuNTU3LjA2OC0zOTcuOTQ0TDM4MCA4MC41N2wtLjA2OSAzOTcuOTQ0IiBzdHlsZT0iZmlsbDojMDAwO2ZpbGwtb3BhY2l0eToxIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSg0Ny43MTIgLjQ0MykiLz48cGF0aCBmaWxsPSIjRUI3MTM5IiBkPSJNODYuNTgyIDE1MS4yNjN2Mzk3LjA4MmMtOC45NDMuMDA2LTYyLjk4NiAyLjEwNC04Ni41ODItNjEuNTI5Vjg1LjM4YzE3LjIyOCA2My43OTEgODYuNTgyIDY1Ljg4MyA4Ni41ODIgNjUuODgzeiIgc3R5bGU9ImZpbGw6IzAwMDtmaWxsLW9wYWNpdHk6MSIgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNDcuNzEyIC40NDMpIi8%2BPHBhdGggZmlsbD0iI0Y2Qzc2OCIgZD0iTTMxMS42MTggMS44OFYzNy45TDQwLjYxNSAxMTAuNTE1Yy04LjQwOS03Ljk3OC0xNS4zNS0xOC4wNjItMjAuNjQzLTMwLjUwNFoiIHN0eWxlPSJmaWxsOiMwMDA7ZmlsbC1vcGFjaXR5OjEiIHRyYW5zZm9ybT0idHJhbnNsYXRlKDQ3LjcxMiAuNDQzKSIvPjxwYXRoIGZpbGw9IiNmZmYiIGQ9Ik0xNDQuNTE2IDEzMC4zMTZzLTM2LjY3OC0xLjIwMi01Ni41Mi0xOS44NDFsMjcxLjE3Mi03Mi4xNTIgMzYuNjc3IDI2LjQ1NVoiLz48L3N2Zz4%3D&labelColor=02B9D9&color=1C0F0D)](https://get.specstory.com)

# Keyframe Blogger

Convert instructional videos into blog posts by extracting key frames and using AI for content generation.

![Example Blog Generation](media/example-blog.gif)

## Overview

This project processes videos through three steps:
1. **Frame Extraction**: Extract key frames based on transcript analysis
2. **Visual Summary**: Create HTML/Markdown previews with frames + transcript
3. **AI Blog Generation**: Use Gemini to create a polished blog post

## Prerequisites

- Python 3.9+
- MP4 video file + matching SRT transcript (e.g., from Tella)
- FFmpeg installed locally
- Gemini API key (get one free at https://aistudio.google.com/apikey)

## Setup

1. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Ready to use!**
   All commands should be prefixed with `poetry run` (as shown in the examples below)

4. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

5. **Set up Gemini API key**:
   - Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)
   - Copy `.env.example` to `.env` and add your API key:
     ```bash
     cp .env.example .env
     # Edit .env and replace 'your-api-key-here' with your actual API key
     ```

## Workflow

### 1. Organize Your Video Files

Create a directory for your video project and add your files:

```bash
# Create project directory
mkdir building-a-mintlify-alternative-with-AI-Part-1

# Copy your Tella exports
cp your-video.mp4 building-a-mintlify-alternative-with-AI-Part-1/
cp your-video.srt building-a-mintlify-alternative-with-AI-Part-1/
```

> **Note**: If you have transcripts in other formats (VTT, TXT, etc.), you can convert them to SRT using tools like [FFmpeg](https://ffmpeg.org/) (`ffmpeg -i input.vtt output.srt`) or online converters like [Subtitle Edit](https://www.nikse.dk/SubtitleEdit/).

### 2. Extract Frames

```bash
poetry run python scripts/extract_frames.py building-a-mintlify-alternative-with-AI-Part-1
```

**What it does**:
- Automatically finds MP4 and SRT files in the directory
- Parses SRT to identify complete thoughts (sentences ending with `.`, `?`, `!`)
- Extracts frames at semantically meaningful moments:
  - When a complete sentence/thought is expressed
  - At least 5 seconds apart (to avoid redundancy)
  - OR when important content appears (text > 50 characters)

**Options**:
- `--interval 5.0` - Minimum seconds between frames (default: 5.0)

**Output** (in `building-a-mintlify-alternative-with-AI-Part-1/frames/`):
- Frame images (`frame_0000.jpg`, `frame_0001.jpg`, etc.)
- `frame_data.json` - Frame metadata with timestamps
- `all_subtitles.json` - Complete parsed transcript

### 3. Create Visual Summaries

```bash
poetry run python scripts/create_visual_summary.py building-a-mintlify-alternative-with-AI-Part-1
```

![Full Transcript with Visual Markers](media/full_transcript_with_visual_markers.png)

**What it does**:
- Checks if frames exist (runs extract_frames.py automatically if needed)
- Creates visual representations of your video content
- Uses directory name as the video title

**Output** (in the `frames/` subdirectory):
1. **visual_transcript.html** - Interactive web page with:
   - Full transcript with embedded frame images
   - Table of contents for navigation
   - Clickable images for full-screen view

2. **visual_transcript.md** - Markdown version with:
   - Full transcript with frame markers
   - Embedded images at correct timestamps

3. **api_frame_data.json** - API-ready format with:
   - Segmented transcript (text between frames)
   - Frame metadata and paths
   - Full transcript as single string

### 4. Generate Blog Post with AI

```bash
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1
```

**Options**:
- `--max-frames` - Limit frames if needed (default: use all frames)
- `--model` - Model choice (default: gemini-2.5-pro)
- `--prompt` - Path to custom blog prompt markdown file (default: BLOG_PROMPT.md in current directory)
- `--use-files-api` - Use [Files API](https://ai.google.dev/gemini-api/docs/files) to upload images instead of inline encoding (default: inline)
- `--delete-uploads` - Delete uploaded files after generation (only with --use-files-api, default: keep files)

> **Note**: The default inline encoding is faster and works well even with ~100MB of local image content, despite Google's documentation suggesting the Files API for content over 20MB.

**Examples**:
```bash
# Use all frames with Gemini 2.5 Pro (recommended)
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1

# Use a faster model with limited frames
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1 --model gemini-2.0-flash-exp --max-frames 50

# Use a custom blog prompt file
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1 --prompt custom_prompt.md

# Use Files API for large videos (uploads images to Gemini)
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1 --use-files-api

# Use Files API and clean up after generation
poetry run python scripts/process_with_ai.py building-a-mintlify-alternative-with-AI-Part-1 --use-files-api --delete-uploads
```

**What it does**:
- Loads blog writing style from `BLOG_PROMPT.md` (default) or custom prompt file
- Sends all frames + full transcript to Gemini 2.5 Pro
- Generates blog post named after your directory
- Analyzes which frames are referenced in the generated blog
- Copies only referenced frames to the output directory
- Updates image paths in the blog to point to local copies

**Output Structure**:
```
building-a-mintlify-alternative-with-AI-Part-1/
└── output/
    ├── building-a-mintlify-alternative-with-AI-Part-1.md  # Blog post
    └── building-a-mintlify-alternative-with-AI-Part-1/    # Referenced frames only
        ├── frame_0006.jpg
        ├── frame_0142.jpg
        └── ...
```

## Example Directory Structure

After processing, your project directory will look like:

```
building-a-mintlify-alternative-with-AI-Part-1/
├── your-video.mp4
├── your-video.srt
├── frames/
│   ├── frame_0000.jpg
│   ├── frame_0001.jpg
│   ├── ...
│   ├── frame_data.json
│   ├── all_subtitles.json
│   ├── visual_transcript.html
│   ├── visual_transcript.md
│   └── api_frame_data.json
└── output/
    ├── building-a-mintlify-alternative-with-AI-Part-1.md
    └── building-a-mintlify-alternative-with-AI-Part-1/
        ├── frame_0006.jpg  # Only referenced frames
        ├── frame_0142.jpg
        └── ...
```

## Frame Selection Logic

The script captures frames at moments when:
- A complete thought or sentence has been expressed
- Enough time has passed to avoid similar frames (default: 5 seconds)
- OR when there's particularly important/lengthy content (>50 characters)

This ensures frames are captured at **semantically meaningful moments** rather than fixed intervals.

## Customization

### Adjust Frame Extraction Interval

```bash
# Extract frames with 10-second minimum interval
poetry run python scripts/extract_frames.py your-directory --interval 10.0
```

### Process Multiple Videos

Simply create separate directories for each video:

```bash
poetry run python scripts/extract_frames.py video-project-1
poetry run python scripts/extract_frames.py video-project-2
poetry run python scripts/create_visual_summary.py video-project-1
poetry run python scripts/create_visual_summary.py video-project-2
poetry run python scripts/process_with_ai.py video-project-1
poetry run python scripts/process_with_ai.py video-project-2
```

### Customize Blog Writing Style

Edit `BLOG_PROMPT.md` to adjust:
- Writing tone and style
- Section structure
- Technical detail level
- Image usage guidelines

## Benefits

1. **Cost Efficiency**: 
   - Process hour-long videos for pennies instead of dollars
   - Only send key frames to AI (not entire video)
   - Leverage Gemini 2.5 Pro's large context window

2. **Flexibility**:
   - Work with any video + SRT combination
   - Adjust frame selection criteria
   - Process locally without API limits

3. **Quality**:
   - Frames captured at meaningful moments
   - Full transcript preserved
   - Visual + text context for better AI understanding

## Tips

- Name your directories descriptively (they become the blog title)
- Keep MP4 and SRT filenames consistent for easier management
- Review the HTML preview before generating the blog post
- The blog prompt can be customized in `BLOG_PROMPT.md`
- Only frames referenced in the blog are copied to output (saves space)
- Frame numbering starts at 0 (Frame 0, Frame 1, etc.)

## File Structure

Key files in this project:
- `extract_frames.py` - Extracts frames from video based on transcript
- `create_visual_summary.py` - Creates HTML/MD previews
- `process_with_ai.py` - Generates blog post using Gemini
- `BLOG_PROMPT.md` - Defines blog writing style (shared across all videos)

## Future
- In a draft blog post, deep link from images to their matching time in the video (e.g. on YouTube)
- Customizable link paths for images included in the draft blog post

---

<div align="center">
  <a href="https://bearclaude.specstory.com">
    <img src="media/bearclaude.png" alt="BearClaude" width="24" height="24">
    <br>
    Made with BearClaude
  </a>
</div>
