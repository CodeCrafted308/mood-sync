import os
import base64
import json
import asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import pathlib

load_dotenv(os.path.join(pathlib.Path(__file__).parent.parent, ".env"))

app = FastAPI()

# Enable CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client
# Assumes GEMINI_API_KEY is set in environment
try:
    client = genai.Client()
except Exception as e:
    client = None
    print(f"Warning: Failed to initialize Gemini client. Error: {e}")

class ImagePayload(BaseModel):
    image_base64: str

@app.post("/api/analyze")
async def analyze_mood(payload: ImagePayload):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini client not initialized. Check API key.")
    
    try:
        # Decode the base64 image
        # The frontend will send a data URL like "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
        base64_data = payload.image_base64
        if "," in base64_data:
            base64_data = base64_data.split(",")[1]
            
        image_bytes = base64.b64decode(base64_data)
        
        prompt = """
        Analyze this image of a person working.
        Detect the primary emotion and recommend a song using the following mapping:

        Detected Emotion,Music Genre Recommendation,Tempo (BPM),Tone/Key
        Happy,Dance / Pop / Funk,110–130,Major Keys
        Sad,Soul / Folk / Classical,60–80,Minor Keys
        Angry,Metal / Hard Techno / Punk,140+,Dissonant/Heavy
        Neutral,Lo-Fi / Downtempo,80–100,Balanced/Steady
        Anxious,Nature Sounds / Meditative,<60,Harmonic/Pure

        Use this mapping to choose a song suggestion and describe the mood.
        Also provide a HEX color code that matches this vibe.

        Your response MUST be a valid JSON object with the following keys:
        - "mood_analysis": A short 1-2 sentence description of the user's mood and state.
        - "song_suggestion": A specific real-world song recommendation (e.g., "Weightless by Marconi Union").
        - "music_genre": A short genre recommendation from the mapping.
        - "tempo_bpm": The tempo range or BPM suggestion.
        - "tone_or_key": The tone or key style recommendation.
        - "hex_color": A valid CSS hex color code (e.g., "#1E90FF") that represents the vibe.
        - "mood_category": A single word categorization of the mood. MUST be exactly one of: "happy", "sad", "angry", "neutral", "anxious".
        """
        # Retry logic for 503 Overloaded errors
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                # Parse the JSON response and validate required fields
                result_json = json.loads(response.text)
                required_keys = [
                    "mood_analysis",
                    "song_suggestion",
                    "music_genre",
                    "tempo_bpm",
                    "tone_or_key",
                    "hex_color",
                    "mood_category",
                ]
                missing = [key for key in required_keys if key not in result_json]
                if missing:
                    raise ValueError(f"Missing required response fields: {', '.join(missing)}")
                if result_json.get("mood_category") not in {"happy", "sad", "angry", "neutral", "anxious"}:
                    raise ValueError("Invalid mood_category returned")
                return result_json
            except Exception as e:
                if "503" in str(e) and attempt < max_retries - 1:
                    print(f"API overloaded (503). Retrying in 2 seconds... (Attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(2)
                else:
                    raise e # Re-raise to be caught by the outer block
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Returning mock data fallback since the API call failed.")
        
        # Fallback Mock Response so the UI still functions for testing
        mock_response = {
            "mood_analysis": "You look like you're in a positive, happy mood with good energy. (MOCK DATA - Check API Key)",
            "song_suggestion": "Uptown Funk by Mark Ronson ft. Bruno Mars",
            "music_genre": "Dance / Pop / Funk",
            "tempo_bpm": "110-130",
            "tone_or_key": "Major Keys",
            "hex_color": "#FFB600",
            "mood_category": "happy"
        }
        return mock_response

# Mount frontend static files
# We mount this at the root so that / serves index.html
frontend_dir = os.path.join(pathlib.Path(__file__).parent.parent, "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
