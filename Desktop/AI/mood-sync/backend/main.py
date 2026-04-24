import os
import base64
import json
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
        What is their mood? 
        Recommend a specific 30-second "Lyria 3" style music track to boost their focus based on their mood.
        Also provide a HEX color code that matches this vibe.
        
        Your response MUST be a valid JSON object with the following keys:
        - "mood_analysis": A short 1-2 sentence description of the user's mood and state.
        - "lyria_track_suggestion": A description of the suggested Lyria 3 focus track (e.g., "Ambient lo-fi beats with a gentle bassline").
        - "hex_color": A valid CSS hex color code (e.g., "#1E90FF") that represents the vibe.
        """
        
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
        
        # Parse the JSON response
        result_json = json.loads(response.text)
        return result_json
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Returning mock data fallback since the API call failed.")
        
        # Fallback Mock Response so the UI still functions for testing
        mock_response = {
            "mood_analysis": "You look like you're deeply focused but could use a burst of energy! (MOCK DATA - Check API Key)",
            "lyria_track_suggestion": "Upbeat synthwave with a driving bassline to keep the momentum going.",
            "hex_color": "#FF007F"
        }
        return mock_response

# Mount frontend static files
# We mount this at the root so that / serves index.html
frontend_dir = os.path.join(pathlib.Path(__file__).parent.parent, "frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
