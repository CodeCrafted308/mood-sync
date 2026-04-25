# Mood Sync: AI-Powered Environment Adapter

Mood Sync is a real-time web application that monitors your facial expressions via webcam, using Google's Gemini AI to detect your mood. Based on this analysis, the system instantly triggers adaptive environment changes—suggesting a tailored "Lyria 3" style focus music track and generating a dynamic HEX color to adjust your room's smart lighting or screen vibe.

## Features

- **Real-Time Webcam Integration:** Captures live snapshots directly from your browser.
- **AI Mood Analysis:** Uses the powerful `gemini-2.5-flash` model to analyze your current state and mood based on visual cues.
- **Adaptive Music Suggestions:** Generates customized 30-second music track suggestions tailored to improve focus or match your energy.
- **Dynamic Color Generation:** Provides a custom HEX color code corresponding to your mood vibe, instantly updating the app's aesthetic.
- **Mock Audio Player:** An interactive UI to simulate playing the generated focus track.

## Tech Stack

- **Frontend:** Vanilla HTML, CSS, JavaScript
- **Backend:** Python, FastAPI, Uvicorn
- **AI Integration:** Google GenAI SDK (`gemini-2.5-flash`)
- **Other Tools:** Pydantic, python-dotenv

## Prerequisites

- Python 3.8+
- A Google Gemini API Key

## Setup & Installation

1. **Clone the repository (or navigate to the project folder):**
   ```bash
   cd mood-sync
   ```

2. **Create a virtual environment (Optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   Navigate to the backend directory and install the required Python packages.
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory (`mood-sync/.env`) and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

## Usage

1. **Start the backend server:**
   From the `backend` directory, run:
   ```bash
   python main.py
   # OR
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the application:**
   Open your browser and navigate to ``. The FastAPI server serves the static frontend files directly.

3. **Analyze your mood:**
   - Grant the browser permission to access your webcam.
   - Click the **"Analyze My Mood"** button.
   - Wait for the AI to process the image. The UI will update with your mood analysis, a music track suggestion, and it will change the theme color based on the generated HEX code!

## Architecture Flow

1. The frontend captures a frame from the webcam feed and converts it to a base64 encoded JPEG.
2. This image is sent via a POST request to the FastAPI `/api/analyze` endpoint.
3. The backend constructs a prompt and passes the image to the `gemini-3.0-flash` model via the GenAI SDK.
4. The AI returns a structured JSON payload containing the mood description, music suggestion, and HEX color.
5. The frontend parses this JSON and dynamically updates the DOM and CSS variables to reflect the new vibe.
http://localhost:8000