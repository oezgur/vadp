from fastapi import FastAPI, WebSocket
import uvicorn
import pyaudio
import webrtcvad
from fastapi.middleware.cors import CORSMiddleware
import datetime
from fastapi.responses import JSONResponse
from fastapi import FastAPI, WebSocket, File, UploadFile

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

"""

@app.post("/")
async def root():
    return {"message": "Hello World"}
"""
@app.post("/")
async def root(audio: UploadFile = File(...)):
    # Save the audio file
    file_path = f"audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    with open(file_path, "wb") as buffer:
        buffer.write(await audio.read())
    return JSONResponse(content={"message": "Audio received and saved"})




@app.post("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    vad = webrtcvad.Vad(3)  # VAD agresiflik seviyesini ayarla (0-3 arası)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=320)
    
    try:
        while True:
            frame = stream.read(320)
            is_speech = vad.is_speech(frame, 16000)
            message = "Speaking" if is_speech else "Not speaking"
            print(message)  # Konsola loglama
            await websocket.send_text(message)
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()
    return {"message": "Audio recived"}

@app.websocket("/audio")
async def save_audio(websocket):
    file_path = f"audio_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
    try:
        with open(file_path, 'wb') as audio_file:
            while True:
                try:
                    audio_data = await websocket.receive_bytes()
                    if not audio_data:
                        break
                    audio_file.write(audio_data)
                except Exception as e:
                    print(f"Error receiving audio data: {e}")
                    break
    except Exception as e:
        print(f"Error saving audio: {e}")
        return {"message": "Error saving audio"}
    return {"message": "Audio saved successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


