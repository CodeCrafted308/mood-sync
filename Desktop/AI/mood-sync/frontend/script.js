document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('snapshotCanvas');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const scanner = document.getElementById('scanner');
    const cameraStatus = document.getElementById('cameraStatus');
    
    // Result elements
    const moodText = document.getElementById('moodText');
    const trackText = document.getElementById('trackText');
    const colorSwatch = document.getElementById('colorSwatch');
    const colorHex = document.getElementById('colorHex');
    const vibeOverlay = document.getElementById('vibeOverlay');
    
    // Audio Player elements
    const playBtn = document.getElementById('playBtn');
    const progressBar = document.getElementById('progressBar');
    
    let stream = null;
    let isPlaying = false;
    let audioInterval;
    
    // Add placeholder audio tracks mapped to moods
    const audioTracks = {
        'happy': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', // Upbeat and happy
        'sad': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', // Slower, melancholy
        'focused': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', // Steady, ambient
        'energetic': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3', // Fast, high energy
        'relaxed': 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3' // Chill, slow
    };
    let currentAudio = new Audio(audioTracks['focused']);
    currentAudio.loop = true;

    // Initialize Webcam
    async function initCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 1280, height: 720, facingMode: "user" } 
            });
            video.srcObject = stream;
            cameraStatus.textContent = "Camera Active";
            cameraStatus.style.color = "#4ade80";
            cameraStatus.style.borderColor = "rgba(74, 222, 128, 0.3)";
        } catch (err) {
            console.error("Error accessing webcam: ", err);
            cameraStatus.textContent = "Camera Error: " + (err.name || err.message);
            cameraStatus.style.color = "#ef4444";
            cameraStatus.style.borderColor = "rgba(239, 68, 68, 0.3)";
            analyzeBtn.disabled = true;
        }
    }

    // Call init
    initCamera();

    // Mock Audio Player Logic with Placeholder Sound
    playBtn.addEventListener('click', () => {
        isPlaying = !isPlaying;
        
        if (isPlaying) {
            currentAudio.play().catch(e => console.log("Audio play blocked by browser:", e));
            playBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>';
            let progress = 0;
            audioInterval = setInterval(() => {
                progress += (100 / 300); // 30 seconds = 300 * 100ms
                if (progress >= 100) {
                    progress = 0;
                    isPlaying = false;
                    clearInterval(audioInterval);
                    currentAudio.pause();
                    currentAudio.currentTime = 0;
                    playBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
                }
                progressBar.style.width = `${progress}%`;
            }, 100);
        } else {
            currentAudio.pause();
            playBtn.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>';
            clearInterval(audioInterval);
        }
    });

    // Capture and Analyze
    analyzeBtn.addEventListener('click', async () => {
        if (!stream) return;

        // UI Feedback
        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";
        scanner.classList.add('active');
        
        // Take Snapshot
        const ctx = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Get base64 JPEG
        const base64Image = canvas.toDataURL('image/jpeg', 0.8);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image_base64: base64Image })
            });

            if (!response.ok) {
                throw new Error(`Server responded with ${response.status}`);
            }

            const data = await response.json();
            
            // Update UI with results
            moodText.textContent = data.mood_analysis;
            trackText.textContent = data.song_suggestion;
            
            // Update Vibe Color
            const hex = data.hex_color;
            colorHex.textContent = hex;
            colorSwatch.style.backgroundColor = hex;
            colorSwatch.style.boxShadow = `0 0 20px ${hex}`;
            
            // Update CSS Variables for app-wide vibe
            document.documentElement.style.setProperty('--vibe-color', hex);
            document.documentElement.style.setProperty('--accent-color', hex);
            vibeOverlay.style.opacity = '0.3';
            
            // Select a new audio track based on the mood category
            const category = data.mood_category || 'focused';
            currentAudio.src = audioTracks[category] || audioTracks['focused'];
            
            // Reset audio player if playing
            if (isPlaying) playBtn.click();
            progressBar.style.width = '0%';

        } catch (error) {
            console.error("Analysis Error:", error);
            moodText.textContent = "Error analyzing mood. Check console and API keys.";
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analyze My Mood";
            scanner.classList.remove('active');
        }
    });
});
