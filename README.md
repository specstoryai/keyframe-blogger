# Video Transcriber with Frame Extraction and AI Processing

A two-step approach to efficiently process long instructional videos to create matching blog posts: extract key frames locally, then use AI for analysis.

## Overview

This project processes videos by:
1. **Local Processing**: Extract key frames and parse SRT transcript
2. **AI Enhancement**: Send selected frames + transcript to Gemini for blog post generation

This approach dramatically reduces API costs compared to sending entire videos.

## Prerequisites

- Python 3.8+
- MP4 video file
- Matching SRT transcript file (e.g., from Tella)
- FFmpeg installed locally
- Google Cloud account (for AI processing)

## Setup

1. **Install dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install google-cloud-aiplatform
   ```

2. **Install FFmpeg** (if not already installed):
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

3. **Configure Google Cloud** (for AI processing):
   - Create a Google Cloud project
   - Enable the Vertex AI API
   - Set up authentication:
     ```bash
     gcloud auth application-default login
     ```
   - Set environment variables:
     ```bash
     export GOOGLE_CLOUD_PROJECT="your-project-id"
     ```

## Usage

### Step 1: Extract Frames and Parse Transcript

```bash
python extract_frames.py
```

**Inputs**:
- `BuildingTnyDocs-ADocsSiteMicroSaaS.mp4` (or modify the filename in the script)
- `BuildingTnyDocs-ADocsSiteMicroSaaS.srt` (matching SRT file)

**How it works**:
- Parses the SRT file to identify complete thoughts (sentences ending with `.`, `?`, `!`)
- Extracts frames at semantically meaningful moments:
  - When a complete sentence/thought is expressed
  - At least 5 seconds apart (to avoid redundancy)
  - OR when important content appears (text > 50 characters)

**Outputs**:
- `frames/` directory with extracted JPG images
- `frame_data.json` - Frame metadata with timestamps
- `all_subtitles.json` - Complete parsed transcript

### Step 2: Create Visual Summaries

```bash
python create_visual_summary.py
```

**Outputs**:
1. **visual_transcript.html** - Interactive web page with:
   - Full transcript with embedded frame images
   - Table of contents for navigation
   - Clickable images for full-screen view

2. **visual_transcript.md** - Markdown version with:
   - Full transcript with frame markers
   - Embedded images at correct timestamps
   - Ready for documentation/sharing

3. **api_frame_data.json** - API-ready format with:
   - Segmented transcript (text between frames)
   - Frame metadata and paths
   - Full transcript as single string
   - Ready for Gemini API consumption

### Step 3: Generate Blog Post with AI

```bash
python process_with_ai.py
```

**Options**:
- `--max-frames` - Limit frames if needed (default: use all frames)
- `--model` - Model choice (default: gemini-2.5-pro)
- `--output` - Output filename (default: blog_post.md)

**Examples**:
```bash
# Use all frames with Gemini 2.5 Pro (recommended)
python process_with_ai.py

# Use a faster model with limited frames
python process_with_ai.py --model gemini-2.0-flash-exp --max-frames 50
```

**How it works**:
1. Loads the blog writing prompt from `BLOG_PROMPT.md`
2. Combines full transcript + all frame images (up to 460)
3. Leverages Gemini 2.5 Pro's large context window (2M tokens)
4. Generates a standalone blog post with proper structure

**Output**: A complete blog post in Markdown format with:
- Engaging title and introduction
- Logical sections with headers
- Embedded frame references
- Code snippets and technical details
- Professional technical writing style

## Benefits of This Approach

1. **Cost Efficiency**: 
   - Process hour-long videos for pennies instead of dollars
   - Only send key frames (460 frames → ~245 key frames)
   - Include transcript context without video overhead

2. **Flexibility**:
   - Choose which frames to include
   - Adjust frame selection criteria
   - Process locally without API limits

3. **Quality**:
   - Frames captured at meaningful moments
   - Full transcript preserved
   - Visual + text context for better AI understanding

## Customization

To process your own videos:

1. Update filenames in `extract_frames.py`:
   ```python
   video_file = "your_video.mp4"
   srt_file = "your_transcript.srt"
   ```

2. Adjust frame selection criteria:
   ```python
   key_frames = get_key_frames(subtitles, interval=5.0)  # Change interval
   ```

3. Modify frame selection logic in `get_key_frames()` function
