#!/usr/bin/env python3
"""
Video Transcriber using Google Vertex AI Gemini - Direct GCS version
"""

import os
import sys
import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig

# Configuration
PROJECT_ID = "gen-lang-client-0461843917"
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-pro"  # Gemini 2.5 Pro model
GCS_URI = "gs://gemini-video-transcribe-1752197890/videos/BuildingTnyDocs-ADocsSiteMicroSaaS.mp4"

def transcribe_video_from_gcs():
    """
    Transcribe a video directly from GCS using Gemini.
    """
    print(f"Initializing Vertex AI in project: {PROJECT_ID}")
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print(f"Loading model: {MODEL_NAME}")
    model = GenerativeModel(MODEL_NAME)
    
    # Create video part from GCS URI
    print(f"Creating video reference from: {GCS_URI}")
    video_part = Part.from_uri(
        uri=GCS_URI,
        mime_type="video/mp4"
    )
    
    # Generation config
    generation_config = GenerationConfig(
        temperature=0.1,
        max_output_tokens=8192,
    )
    
    # Transcription prompt with FPS instructions
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

    print("Sending video to Gemini for transcription...")
    print(f"Using model: {MODEL_NAME}")
    print("This may take a few minutes for an hour-long video...")
    
    try:
        response = model.generate_content(
            [video_part, prompt],
            generation_config=generation_config,
            stream=False
        )
        
        print("\nTranscription completed successfully!")
        
        # Save output
        output_path = "transcription_output.md"
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
        print(f"\nError during transcription: {e}")
        if hasattr(e, 'message'):
            print(f"Error details: {e.message}")
        if "quota" in str(e).lower():
            print("\nTip: You may have hit a quota limit. Try:")
            print("  1. Using gemini-1.5-flash-002 instead of pro")
            print("  2. Waiting a few minutes")
            print("  3. Checking your quota at: https://console.cloud.google.com/apis/api/aiplatform.googleapis.com/quotas")
        raise

if __name__ == "__main__":
    transcribe_video_from_gcs()