import React, { useRef, useEffect } from 'react';
import axiosInstance from '../../axiosConfig.js'

const AudioVisualizer = () => {
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const bufferLengthRef = useRef(null);
  const sourceRef = useRef(null);

  // List available media devices and choose a specific one
  async function listAndSelectMediaDevice() {
    const devices = await navigator.mediaDevices.enumerateDevices();
    let audioInputDeviceId = null;

    devices.forEach(device => {
      console.log(`${device.kind}: ${device.label} (ID: ${device.deviceId})`);
      // Choose the first audio input device (microphone)
      if (device.label === 'Domyślny - Internal Microphone (Built-in)') {
        audioInputDeviceId = device.deviceId;
      }
    });

    return audioInputDeviceId;
  }

  useEffect(() => {
    const init = async () => {
      try {
        // Get the deviceId of a specific microphone
        const selectedDeviceId = await listAndSelectMediaDevice();

        if (!selectedDeviceId) {
          console.error("No audio input devices found.");
          return;
        }
       
        // Access the microphone
        const stream = await navigator.mediaDevices.getUserMedia({ audio: { deviceId: selectedDeviceId  } });
        audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        analyserRef.current = audioContextRef.current.createAnalyser();
        sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);

        sourceRef.current.connect(analyserRef.current);
        analyserRef.current.fftSize = 2048;
        bufferLengthRef.current = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLengthRef.current);

        draw();
      } catch (err) {
        console.error('Error accessing the microphone', err);
      }
    };

    const draw = () => {
      requestAnimationFrame(draw);

      analyserRef.current.getByteTimeDomainData(dataArrayRef.current);

      const canvas = canvasRef.current;
      const canvasCtx = canvas.getContext('2d');
      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);

      // Create gradient
      const gradient = canvasCtx.createLinearGradient(0, 0, canvas.width, 0);
      gradient.addColorStop(0, 'rgb(66, 135, 245, 0)');
      gradient.addColorStop(0.2, '#fb8c00');
      gradient.addColorStop(0.5, '#568166');
      gradient.addColorStop(0.8, '#fb8c00');
      gradient.addColorStop(1, 'rgb(66, 135, 245, 0)');

      canvasCtx.fillStyle = 'rgb(0, 0, 0, 0)';
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

      canvasCtx.lineWidth = 2;
      canvasCtx.strokeStyle = gradient;

      canvasCtx.beginPath();

      const sliceWidth = (canvas.width * 1.0) / bufferLengthRef.current;
      let x = 0;

      for (let i = 0; i < bufferLengthRef.current; i++) {
        const v = dataArrayRef.current[i] / 128.0;
        const y = (v * canvas.height) / 2 ;

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
    };

    init();

    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return <canvas ref={canvasRef} width="600" height="90" />;
};

export default AudioVisualizer;