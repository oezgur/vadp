import React, { useState } from 'react';
import axios from 'axios';

function Voice() {
  const [isListening, setIsListening] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [response, setResponse] = useState('');

  const startListening = async () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        recorder.ondataavailable = handleAudioData;
        recorder.start();
        setMediaRecorder(recorder);
        setIsListening(true);
      } catch (err) {
        console.error('Error accessing the microphone:', err);
      }
    } else {
      console.error('getUserMedia not supported on your browser!');
    }
  };

  const stopListening = () => {
    if (mediaRecorder) {
      mediaRecorder.stop(); // This will trigger the `ondataavailable` event
      setIsListening(false);
    }
  };

  const handleAudioData = async (event) => {
    if (event.data.size > 0) {
      sendAudioData(event.data);
    }
  };

  const sendAudioData = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'audio.wav');
    
    try {
      const response = await axios.post('http://127.0.0.1:8000', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResponse(response.data);
    } catch (error) {
      console.error('Error sending audio data:', error);
    }
  };

  return (
    <div>
      <button onClick={!isListening ? startListening : stopListening}>
        {!isListening ? 'Start Listening' : 'Stop Listening'}
      </button>
      {response && <p>Response: {response.message}</p>}
    </div>
  );
}

export default Voice;