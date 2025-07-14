#!/usr/bin/env python3
"""
Video Transcriber using Google Vertex AI Gemini 2.5
Implements the 0.5fps trick to reduce token usage for long videos
"""

import os
import sys
from pathlib import Path
import vertexai
from vertexai.generative_models import GenerativeModel, Part, VideoMetadata, GenerationConfig

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gen-lang-client-0461843917")
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.0-flash-exp"  # or "gemini-1.5-pro-002" for production

def transcribe_video_local(video_path: str, output_path: str):
    """
    Transcribe a local video file using Gemini with reduced FPS for token efficiency.
    """
    print(f"Initializing Vertex AI in project: {PROJECT_ID}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print(f"Loading model: {MODEL_NAME}")
    model = GenerativeModel(MODEL_NAME)
    
    # Read video file
    print(f"Reading video file: {video_path}")
    video_file = Part.from_data(
        data=open(video_path, "rb").read(),
        mime_type="video/mp4"
    )
    
    # Configure video metadata with 0.5 fps to reduce tokens
    video_metadata = VideoMetadata(
        start_offset="0s",
        end_offset=None,  # Process entire video
        fps=0.5  # Key optimization: reduces frame sampling
    )
    
    # Set the video metadata
    video_file.video_metadata = video_metadata
    
    # Generation config for low resolution to further reduce tokens
    generation_config = GenerationConfig(
        temperature=0.1,
        max_output_tokens=8192,
    )
    
    # Transcription prompt
    prompt = """You are Jake Levirne, founder of SpecStory and an impatient, plain-spoken tech optimist.  
Your job is to turn the attached hour-long screen-share (audio + video) into a developer-ready blog post.

**Audience**  
• Senior product-minded engineers and AI-curious product managers.  
• They skim first, then dive deep.

**Voice & style**  
• Conversational but incisive, like the sample "All that's left is care".  
• Use short punchy sentences, rhetorical questions, and the occasional "here's the rub".  
• Prefer active voice and second-person where possible (Google dev style §Voice)  
• Hide your chain-of-thought and do not mention prompt engineering.

**Structure**  
1. TL;DR box ≤ 120 words.  
2. H₂-level section for each major task shown on screen, in the same order.  
3. Within each H₂ use H₃ sub-steps (Setup, Walk-through, Pitfalls, Next Steps).  
4. Inline every code snippet exactly as seen; wrap blocks in fenced markdown.  
5. Quote the presenter verbatim when they coin a term or give key advice; embed timestamps.  
6. Conclude with three numbered key takeaways.

**Depth & extras**  
• Identify commands, CLI flags, and config files on the screen and explain *why* they matter.  
• When multiple approaches are demoed, compare them in a 2-column pros/cons table.  
• If the video zooms a UI element, capture a still frame and suggest it as a figure caption.  
• Target total length ≈ 1,200 words ±10%.  Trim fluff; readers value crispness over eloquence.

**Output**  
Return pure markdown only. No front-matter. Start writing now."""

    print("Sending video to Gemini for transcription...")
    print(f"Video processing settings: FPS={video_metadata.fps}, Resolution=MEDIUM")
    
    try:
        response = model.generate_content(
            [video_file, prompt],
            generation_config=generation_config
        )
        
        print("Transcription completed successfully!")
        
        # Save output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Output saved to: {output_path}")
        
        # Print token usage if available
        if hasattr(response, 'usage_metadata'):
            metadata = response.usage_metadata
            print(f"\nToken usage:")
            print(f"  Prompt tokens: {metadata.prompt_token_count:,}")
            print(f"  Response tokens: {metadata.candidates_token_count:,}")
            print(f"  Total tokens: {metadata.total_token_count:,}")
        
        return response.text
        
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise

def main():
    # Input and output paths
    video_path = "BuildingTnyDocs-ADocsSiteMicroSaaS.mp4"
    output_path = "transcription_output.md"
    
    # Check if video exists
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Check if Google Cloud project is set
    if PROJECT_ID == "your-project-id":
        print("Error: Please set your Google Cloud project ID in the script or as GOOGLE_CLOUD_PROJECT env var")
        sys.exit(1)
    
    # Run transcription
    transcribe_video_local(video_path, output_path)

if __name__ == "__main__":
    main()