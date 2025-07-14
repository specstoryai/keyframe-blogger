#!/usr/bin/env python3
"""
Video Transcriber using Google Generative AI (AI Studio API)
This uses the generativeai library directly without Vertex AI
"""

import os
import sys
from pathlib import Path
import google.generativeai as genai

# Configuration
API_KEY = os.getenv("GOOGLE_API_KEY")  # You'll need to get this from AI Studio
MODEL_NAME = "models/gemini-1.5-pro"  # Gemini 1.5 Pro with 2M context window

def transcribe_video_local(video_path: str, output_path: str):
    """
    Transcribe a local video file using Google Generative AI.
    """
    global API_KEY
    if not API_KEY:
        print("Please enter your Google AI Studio API key")
        print("Get your API key from: https://aistudio.google.com/apikey")
        API_KEY = input("API Key: ").strip()
        if not API_KEY:
            print("Error: API key is required")
            sys.exit(1)
    
    print(f"Configuring Generative AI with API key...")
    genai.configure(api_key=API_KEY)
    
    print(f"Loading model: {MODEL_NAME}")
    model = genai.GenerativeModel(MODEL_NAME)
    
    # Upload the video file
    print(f"Uploading video file: {video_path}")
    video_file = genai.upload_file(path=video_path, display_name="Screen recording")
    print(f"Uploaded file URI: {video_file.uri}")
    
    # Wait for file to be processed
    print("Waiting for file processing...")
    import time
    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file.name)
        print(".", end="", flush=True)
    
    if video_file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {video_file.state.name}")
    
    print(f"\nFile is ready. State: {video_file.state.name}")
    
    # Generation config
    generation_config = genai.types.GenerationConfig(
        temperature=0.1,
        max_output_tokens=8192,
    )
    
    # Transcription prompt
    prompt = """Process this video as if it were sampled at 0.5 fps to focus on key moments.

You are Jake Levirne, founder of SpecStory and an impatient, plain-spoken tech optimist.  
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

    print("\nSending video to Gemini for transcription...")
    print("This may take a few minutes for an hour-long video...")
    
    try:
        response = model.generate_content(
            [video_file, prompt],
            generation_config=generation_config
        )
        
        print("\nTranscription completed successfully!")
        
        # Save output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"Output saved to: {output_path}")
        
        # Clean up uploaded file
        genai.delete_file(video_file.name)
        print("Cleaned up uploaded file")
        
        return response.text
        
    except Exception as e:
        print(f"\nError during transcription: {e}")
        # Try to clean up file even if error occurs
        try:
            genai.delete_file(video_file.name)
        except:
            pass
        raise

def main():
    # Input and output paths
    video_path = "BuildingTnyDocs-ADocsSiteMicroSaaS.mp4"
    output_path = "transcription_output.md"
    
    # Check if video exists
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Get file size
    file_size = Path(video_path).stat().st_size / (1024 * 1024)  # MB
    print(f"Video file size: {file_size:.1f} MB")
    
    # Run transcription
    transcribe_video_local(video_path, output_path)

if __name__ == "__main__":
    main()