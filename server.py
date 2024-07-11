from fastapi import FastAPI, WebSocket
import uvicorn
import pyaudio
import webrtcvad

app = FastAPI()

@app.websocket("/ws")
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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
