# Video Transcriber with Gemini 2.5

This project transcribes long videos using Google's Gemini 2.5 model with optimizations for token efficiency.

## Setup

1. **Install dependencies**:
   ```bash
   source venv/bin/activate
   pip install google-cloud-aiplatform
   ```

2. **Configure Google Cloud**:
   - Create a Google Cloud project
   - Enable the Vertex AI API
   - Set up authentication (choose one):
     - Option A: Use gcloud CLI: `gcloud auth application-default login`
     - Option B: Use service account key and set `GOOGLE_APPLICATION_CREDENTIALS`

3. **Set environment variables**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GCS_BUCKET="your-bucket-name"  # Only needed for GCS version
   ```

## Usage

### Option 1: Local file processing (simpler, but limited by file size)
```bash
python transcribe_video.py
```

### Option 2: Via Google Cloud Storage (recommended for production)
```bash
python transcribe_video_gcs.py
```

## Token Optimization

The scripts implement several optimizations to handle hour-long videos:

- **FPS reduction**: Set to 0.5 fps instead of default 1 fps (50% token reduction)
- **Resolution**: Can be set to LOW for additional savings
- **Model choice**: Using `gemini-2.0-flash-exp` for faster processing

## Estimated Costs

- 1 hour video at 0.5 fps ≈ 500K tokens
- Gemini 2.5 Flash: ~$1.00 per hour of video
- Gemini 2.5 Pro: ~$1.70 per hour of video

## Output

The transcription will be saved to `transcription_output.md` in the same directory.