import  { useEffect, useRef, useState } from 'react';
import axiosInstance from '../../axiosConfig.js';

function AudioStreamComponent() {
  const [audioData, setAudioData] = useState(null);
  const canvasRef = useRef(null);
  const analyserRef = useRef({ fftSize: 2048 });
  const bufferLengthRef = useRef(analyserRef.current.fftSize / 2);
  const dataArrayRef = useRef(new Uint8Array(bufferLengthRef.current));

  // Fetch data and update `dataArrayRef`
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axiosInstance.get('/audio_stream');
        const audioChannelData = response.data.audio_channel1;
        console.log(response.data.audio_channel1)
        dataArrayRef.current.set(audioChannelData.map(val => Math.min(255, val * 255)));
        setAudioData([...dataArrayRef.current]); // Trigger draw update
      } catch (error) {
        console.error("Error fetching audio stream:", error);
      }
    };

    // Fetch every 500ms
    const intervalId = setInterval(fetchData, 50);
    return () => clearInterval(intervalId);
  }, []);

  // Draw function with continuous animation
  const draw = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const canvasCtx = canvas.getContext('2d');

    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

    // Create gradient
    const gradient = canvasCtx.createLinearGradient(0, 0, canvas.width, 0);
    gradient.addColorStop(0, 'rgba(66, 135, 245, 0)');
    gradient.addColorStop(0.2, '#fb8c00');
    gradient.addColorStop(0.5, '#568166');
    gradient.addColorStop(0.8, '#fb8c00');
    gradient.addColorStop(1, 'rgba(66, 135, 245, 0)');

    canvasCtx.fillStyle = 'rgba(0, 0, 0, 0)';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = gradient;
    canvasCtx.beginPath();

    const sliceWidth = (canvas.width * 1.0) / bufferLengthRef.current;
    let x = 0;

    for (let i = 0; i < bufferLengthRef.current; i++) {
      const v = dataArrayRef.current[i] / 128.0;
      const y = (v * canvas.height) / 2;

      if (i === 0) {
        canvasCtx.moveTo(x, y);
      } else {
        canvasCtx.lineTo(x, y);
      }

      x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();

    // Add label text
    canvasCtx.font = '12px Arial';
    canvasCtx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    canvasCtx.fillText('Raspberry Pi Mic Input', 10, canvas.height - 10);

    requestAnimationFrame(draw); // Continue the animation loop
  };

  // Start the draw loop when the component mounts
  useEffect(() => {
    requestAnimationFrame(draw);
    return () => cancelAnimationFrame(draw); // Cleanup on unmount
  }, []);

  return (
    <>
      <div> {audioData ? '': 'Loading...'} </div>
      <canvas ref={canvasRef} width="600" height="90" ></canvas>
    </>
  );
}

export default AudioStreamComponent;
