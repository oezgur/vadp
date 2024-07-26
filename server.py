from fastapi import FastAPI, File, UploadFile
import uvicorn
import webrtcvad
from fastapi.middleware.cors import CORSMiddleware
import datetime
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import io
import os
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
import logging
import json

app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/")
async def root(audio: UploadFile = File(...)):
    # Save the audio file
    file_path = f"audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    temp_path = file_path + ".tmp"
    wav_path = file_path + ".wav"
    
    # Save uploaded file
    with open(temp_path, "wb") as buffer:
        buffer.write(await audio.read())
    
    # Convert to WAV using pydub
    try:
        audio = AudioSegment.from_file(temp_path)
        audio = audio.set_frame_rate(16000).set_channels(1)  # Ensure 16kHz mono
        audio.export(wav_path, format="wav")
    except Exception as e:
        return JSONResponse(content={"message": f"Error converting audio: {str(e)}"})
    finally:
        os.remove(temp_path)  # Clean up temp file
    
    model = load_silero_vad()
    wav = read_audio(wav_path) # backend (sox, soundfile, or ffmpeg) required!
    speech_timestamps = get_speech_timestamps(wav, model)

    logger.info(f"Speech timestamps: {speech_timestamps}")
    speech_timestamps = json.dumps(speech_timestamps)

    return JSONResponse(content={
        "message": f"Audio processed successfully",
        "vad_result": speech_timestamps
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)