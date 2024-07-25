from fastapi import FastAPI, File, UploadFile
import uvicorn
import webrtcvad
from fastapi.middleware.cors import CORSMiddleware
import datetime
from fastapi.responses import JSONResponse
from pydub import AudioSegment
import io
import os

app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

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
    
    # Perform VAD on the WAV file
    vad = webrtcvad.Vad(3)  # VAD aggressiveness level (0-3)
    
    with open(wav_path, 'rb') as wf:
        audio_data = wf.read()
    
    # Process the audio in 30ms chunks
    chunk_duration = 30  # duration in milliseconds
    sample_rate = 16000
    chunk_size = int(sample_rate * chunk_duration / 1000) * 2  # chunk size in bytes (16-bit audio)
    
    total_chunks = len(audio_data) // chunk_size
    speech_chunks = 0
    
    for i in range(0, total_chunks):
        chunk = audio_data[i*chunk_size:(i+1)*chunk_size]
        is_speech = vad.is_speech(chunk, sample_rate)
        if is_speech:
            speech_chunks += 1
    
    speech_percentage = (speech_chunks / total_chunks) * 100 if total_chunks > 0 else 0
    
    if speech_percentage > 50:
        vad_result = "Significant speech detected"
    else:
        vad_result = "No significant speech detected"
    
    # Clean up WAV file
    os.remove(wav_path)
    
    return JSONResponse(content={
        "message": f"Audio processed successfully",
        "vad_result": vad_result,
        "speech_percentage": f"{speech_percentage:.2f}%"
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)