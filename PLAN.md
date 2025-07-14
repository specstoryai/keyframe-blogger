we're going to try to do the following on the .mp4 video in this project. We probably need to do one of the tricks to reduce the input token size because it's almost an hour long video. try the .5fps. trick. I don't have any of the google utils installed yet but I do have a google cloud account



Below is a clean, end-to-end checklist for turning your hour-long screen-share into a polished blog post with Gemini 2.5 (Pro or Flash) on Vertex AI. Everything else—Assembly, Descript, GPT-4o, etc.—has been stripped away.

⸻

0  Prerequisites

What	Command / Action
Google Cloud project with Vertex AI enabled	gcloud services enable aiplatform.googleapis.com
Gen AI quota for gemini-2.5-pro or gemini-2.5-flash	Request in IAM & Admin → Quotas
Auth (service account or user)	gcloud auth application-default login
SDK (optional Python helper)	pip install google-cloud-aiplatform google-generativeai  ￼


⸻

1  Stage the video in Cloud Storage

# create a bucket once
gsutil mb -l us-central1 gs://my-genai-bucket

# upload your screen-share
gsutil cp screen_share.mp4 gs://my-genai-bucket/

Why? Gemini expects a fileUri that is publicly readable or in the same project. File size must stay ≤ 2 GB per part.  ￼

⸻

2  Plan your token budget (optional but saves money)

Dial	Default	Typical tweak	Effect
fps in videoMetadata	1 fps	0.5 fps for static slides	50 % fewer frame tokens (≈ 150 tokens / s)  ￼
mediaResolution in GenerationConfig	MEDIUM	LOW	66 tokens vs 258 tokens per frame  ￼
startOffset / endOffset	—	Clip intro/outro	Skip irrelevant parts

One hour of default-resolution video ≈ 1 M tokens; that’s the limit for current 1 M-context models. If you need more, lower FPS/resolution or wait for the 2 M-context tier (≈ 2 h at default res).  ￼ ￼

⸻

Here's the prompt we'll use:

```
You are Jake Levirne, founder of SpecStory and an impatient, plain-spoken tech optimist.  
Your job is to turn the attached hour-long screen-share (audio + video) into a developer-ready blog post.

**Audience**  
• Senior product-minded engineers and AI-curious product managers.  
• They skim first, then dive deep.

**Voice & style**  
• Conversational but incisive, like the sample “All that’s left is care”.  
• Use short punchy sentences, rhetorical questions, and the occasional “here’s the rub”.  
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
• Target total length ≈ 1 200 words ±10 %.  Trim fluff; readers value crispness over eloquence.

**Output**  
Return pure markdown only.  No front-matter.  Start writing now.
```

3  Call Gemini 2.5 with REST (curl)

Create request.json:

{
  "contents": [
    {
      "fileData": {
        "fileUri": "gs://my-genai-bucket/screen_share.mp4",
        "mimeType": "video/mp4"
      },
      "videoMetadata": {          // ↓ optional token savers
        "fps": 0.5,
        "startOffset": "0s"
      }
    },
    {
      "text": <prompt here>
    }
  ],
  "generationConfig": {
    "mediaResolution": "MEDIA_RESOLUTION_LOW"
  }
}

Then run:

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d @request.json \
  "https://aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/publishers/google/models/gemini-2.5-pro:generateContent"

The response’s first candidate (candidates[0].content.parts[0].text) is your draft blog post.  ￼ ￼

⸻

4  Same call in Python (Vertex AI SDK)

from vertexai.preview.generative_models import GenerativeModel, Part

model = GenerativeModel("gemini-2.5-pro")

video_part = Part.from_uri(
        uri="gs://my-genai-bucket/screen_share.mp4",
        mime_type="video/mp4",
        video_metadata={"fps": 0.5})

response = model.generate_content(
    [video_part,
     "Write a structured 1200-word blog post (see prompt above)"],
    generation_config={"media_resolution": "MEDIA_RESOLUTION_LOW"})

print(response.text)

A complete sample that summarises a local video lives in Google’s docs.  ￼

⸻

5  Post-process the draft
	•	Fact-check UI labels and proper nouns—OCR errors happen at low FPS.
	•	Run follow-up prompts (“Regenerate just the Troubleshooting section at 250 words”) to refine; every follow-up re-uses the same prompt tokens, so costs are only incremental.
	•	Use Context Caching if you’ll ask many questions about the same hour-long video.  ￼

⸻

6  Cost & latency snapshot

Model	Context window	Price (per 1 M tokens)	Typical latency
Gemini 2.5 Flash	1 M	$2.05 in / $6.50 out	~2–3 s first byte
Gemini 2.5 Pro	1 M (2 M coming)	$3.44 blended	~7 s first byte, faster streaming

Both models cap at ≈ 45 min with audio (≈ 1 h without) unless you down-sample as shown above.  ￼

⸻

7  Troubleshooting checklist
	1.	413 Entity Too Large → video bigger than 2 GB; pre-compress or split.  ￼
	2.	INVALID_ARGUMENT: token limit exceeded → lower fps or set MEDIA_RESOLUTION_LOW.  ￼
	3.	PERMISSION_DENIED → bucket/object not readable by the calling project; run gsutil acl ch -u $(gcloud config get-value account):R gs://....

