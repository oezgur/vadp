import React, { useEffect, useState } from 'react';

const App = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  useEffect(() => {
    // Mikrofon izni isteme
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then((stream) => {
        console.log('Mikrofon izni verildi');

        // WebSocket bağlantısını kurma
        const socket = new WebSocket('ws://localhost:8000/ws');

        socket.onopen = () => {
          console.log('WebSocket connection opened');
        };

        socket.onmessage = (event) => {
          console.log('Message from server:', event.data);  // Mesajları loglama
          setIsSpeaking(event.data === "Speaking");
        };

        socket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setErrorMessage('WebSocket error: ' + error.message);
        };

        socket.onclose = () => {
          console.log('WebSocket connection closed');
        };

        return () => {
          socket.close();
        };
      })
      .catch((error) => {
        console.error('Mikrofon izni reddedildi', error);
        setErrorMessage('Mikrofon izni reddedildi: ' + error.message);
      });
  }, []);

  return (
    <div>
      {errorMessage && <p>{errorMessage}</p>}
      {isSpeaking ? <p>Speaking...</p> : <p>Not speaking...</p>}
    </div>
  );
};

export default App;
