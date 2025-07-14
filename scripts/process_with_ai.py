#!/usr/bin/env python3
import os
import json
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting
from pathlib import Path
import argparse
import sys
import re
import shutil

def encode_image_to_base64(image_path):
    """Encode image file to base64."""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_blog_prompt(prompt_path=None):
    """Load the blog generation prompt."""
    if prompt_path is None:
        # Default to BLOG_PROMPT.md in the current directory
        prompt_path = 'BLOG_PROMPT.md'
    
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Blog prompt file not found at {prompt_path}")
    
    with open(prompt_path, 'r') as f:
        return f.read()

def create_content_parts(api_data, frames_dir, max_frames=None, prompt_path=None):
    """Create content parts for Gemini API from api_frame_data.json."""
    parts = []
    
    # Add the blog prompt
    blog_prompt = load_blog_prompt(prompt_path)
    parts.append(Part.from_text(blog_prompt))
    
    # Add context about the video
    parts.append(Part.from_text(f"\n\n## Video Information\n"
                                f"Title: {api_data['video_title']}\n"
                                f"Duration: {api_data['total_duration']}\n"
                                f"Total Frames Available: {api_data['frame_count']}\n\n"))
    
    # Add full transcript
    parts.append(Part.from_text(f"## Full Transcript\n\n{api_data['full_transcript']}\n\n"))
    
    # Add frame images with their transcript segments
    parts.append(Part.from_text("## Frame Images with Context\n\n"))
    
    # Use all segments or limit if specified
    segments = api_data['segments']
    if max_frames and len(segments) > max_frames:
        # Take every nth frame to get approximately max_frames
        step = len(segments) // max_frames
        selected_segments = segments[::step][:max_frames]
        print(f"Selected {len(selected_segments)} frames out of {len(segments)} total")
    else:
        selected_segments = segments
        print(f"Using all {len(selected_segments)} frames")
    
    # Add each frame with its context
    for i, segment in enumerate(selected_segments):
        # Add frame context
        parts.append(Part.from_text(f"\n### Frame {segment['frame_number']} - [{segment['timestamp']}]\n"
                                   f"Transcript: {segment['transcript_segment']}\n"))
        
        # Add frame image
        try:
            # Image path is relative to frames directory
            image_path = os.path.join(frames_dir, segment['image_path'])
            image_data = encode_image_to_base64(image_path)
            parts.append(Part.from_data(
                mime_type="image/jpeg",
                data=image_data
            ))
        except Exception as e:
            print(f"Warning: Could not load image {segment['image_path']}: {e}")
    
    # Final instruction
    parts.append(Part.from_text("\n\n## Task\n\n"
                               "Based on the above transcript and frame images, "
                               "create a comprehensive blog post following the style guidelines provided. "
                               "Make sure to reference specific frames where relevant and create a "
                               "cohesive narrative that stands on its own."))
    
    return parts

def process_with_gemini(parts, model_name="gemini-2.5-pro"):
    """Send content to Gemini and get blog post."""
    
    # Initialize Vertex AI
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("Please set GOOGLE_CLOUD_PROJECT environment variable")
    
    vertexai.init(project=project_id, location="us-central1")
    
    # Configure model
    model = GenerativeModel(model_name)
    
    # Safety settings
    safety_settings = [
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        ),
        SafetySetting(
            category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
            threshold=SafetySetting.HarmBlockThreshold.OFF
        )
    ]
    
    # Generate content
    print(f"Sending to {model_name}...")
    response = model.generate_content(
        parts,
        safety_settings=safety_settings,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }
    )
    
    # Handle response with multiple parts
    try:
        # Try simple text access first
        return response.text
    except ValueError:
        # If that fails, extract text from parts
        if response.candidates:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                # Combine all text parts
                text_parts = []
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                return '\n'.join(text_parts)
        raise ValueError("Could not extract text from response")

def extract_referenced_frames(blog_content):
    """Extract frame references from the blog post markdown."""
    # Look for patterns like frame_0006.jpg or Frame 6 or [Frame 6]
    frame_patterns = [
        r'frame_(\d+)\.jpg',  # frame_0006.jpg
        r'Frame (\d+)',       # Frame 6
        r'\[Frame (\d+)\]',   # [Frame 6]
    ]
    
    referenced_frames = set()
    for pattern in frame_patterns:
        matches = re.findall(pattern, blog_content, re.IGNORECASE)
        for match in matches:
            frame_num = int(match)
            referenced_frames.add(frame_num)
    
    return sorted(referenced_frames)

def copy_referenced_frames(frames_dir, output_dir, blog_name, referenced_frames):
    """Copy only the referenced frame images to the output directory."""
    # Create subdirectory for images
    images_dir = os.path.join(output_dir, blog_name)
    Path(images_dir).mkdir(parents=True, exist_ok=True)
    
    copied_count = 0
    for frame_num in referenced_frames:
        # Try different filename formats
        possible_filenames = [
            f"frame_{frame_num:04d}.jpg",  # frame_0006.jpg
            f"frame_{frame_num:03d}.jpg",   # frame_006.jpg
            f"frame_{frame_num}.jpg",       # frame_6.jpg
        ]
        
        for filename in possible_filenames:
            src_path = os.path.join(frames_dir, filename)
            if os.path.exists(src_path):
                dst_path = os.path.join(images_dir, filename)
                shutil.copy2(src_path, dst_path)
                print(f"Copied {filename} to output directory")
                copied_count += 1
                break
    
    return copied_count

def update_image_paths_in_blog(blog_content, blog_name):
    """Update image paths in the blog to point to the local copies."""
    # Replace absolute or frames/ paths with relative paths
    updated_content = blog_content
    
    # Pattern to match various image path formats
    # Only update paths that don't already have the blog_name prefix
    patterns = [
        (r'!\[([^\]]*)\]\(frames/(frame_\d+\.jpg)\)', r'![\1](' + blog_name + r'/\2)'),  # ![alt](frames/frame_0001.jpg)
        (r'!\[([^\]]*)\]\((frame_\d+\.jpg)\)', r'![\1](' + blog_name + r'/\2)'),         # ![alt](frame_0001.jpg)
    ]
    
    # Avoid double-processing by checking if path already contains blog_name
    for pattern, replacement in patterns:
        # Only replace if the path doesn't already contain the blog_name
        if blog_name not in updated_content:
            updated_content = re.sub(pattern, replacement, updated_content)
        else:
            # More careful replacement - only if not already prefixed
            lines = updated_content.split('\n')
            for i, line in enumerate(lines):
                if f']({blog_name}/' not in line:  # Not already updated
                    lines[i] = re.sub(pattern, replacement, line)
            updated_content = '\n'.join(lines)
    
    return updated_content

def main():
    parser = argparse.ArgumentParser(description='Generate blog post from video frames and transcript')
    parser.add_argument('directory', help='Directory containing frames subdirectory with extracted data')
    parser.add_argument('--max-frames', type=int, default=None, 
                       help='Maximum number of frames to send to API (default: all frames)')
    parser.add_argument('--model', default='gemini-2.5-pro',
                       help='Gemini model to use (default: gemini-2.5-pro)')
    parser.add_argument('--prompt', type=str, default=None,
                       help='Path to custom blog prompt markdown file (default: BLOG_PROMPT.md in current directory)')
    args = parser.parse_args()
    
    try:
        # Validate directory
        if not os.path.exists(args.directory):
            raise ValueError(f"Directory {args.directory} does not exist")
        
        # Set up paths
        frames_dir = os.path.join(args.directory, "frames")
        api_data_path = os.path.join(frames_dir, "api_frame_data.json")
        
        if not os.path.exists(api_data_path):
            raise ValueError(f"api_frame_data.json not found in {frames_dir}. Run create_visual_summary.py first.")
        
        # Load API data
        print(f"Loading frame data from {api_data_path}...")
        with open(api_data_path, 'r') as f:
            api_data = json.load(f)
        
        # Create content parts
        if args.max_frames:
            print(f"Creating content with up to {args.max_frames} frames...")
        else:
            print(f"Creating content with all available frames...")
        parts = create_content_parts(api_data, frames_dir, max_frames=args.max_frames, prompt_path=args.prompt)
        
        # Process with Gemini
        blog_content = process_with_gemini(parts, model_name=args.model)
        
        # Create output directory
        output_dir = os.path.join(args.directory, "output")
        Path(output_dir).mkdir(exist_ok=True)
        
        # Generate blog filename from directory name
        blog_name = os.path.basename(args.directory)
        blog_filename = f"{blog_name}.md"
        blog_path = os.path.join(output_dir, blog_filename)
        
        # Extract referenced frames
        print("\nAnalyzing blog for frame references...")
        referenced_frames = extract_referenced_frames(blog_content)
        print(f"Found references to {len(referenced_frames)} frames: {referenced_frames}")
        
        # Update image paths in blog
        blog_content = update_image_paths_in_blog(blog_content, blog_name)
        
        # Save blog post
        with open(blog_path, 'w') as f:
            f.write(blog_content)
        
        print(f"\nBlog post generated successfully!")
        print(f"Saved to: {blog_path}")
        
        # Copy referenced frames
        if referenced_frames:
            print(f"\nCopying referenced frames to output directory...")
            copied = copy_referenced_frames(frames_dir, output_dir, blog_name, referenced_frames)
            print(f"Copied {copied} frame images to {os.path.join(output_dir, blog_name)}")
        
        # Show preview
        print("\n" + "="*50)
        print("PREVIEW (first 500 chars):")
        print("="*50)
        print(blog_content[:500] + "...")
        
    except Exception as e:
        print(f"Error generating blog post: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()