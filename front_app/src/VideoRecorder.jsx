import React, { useState, useEffect, useRef } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import * as ffmpeg from 'ffmpeg.wasm';

const VideoRecorder = ({ onVideoSaved }) => {
  const [isRecording, setIsRecording] = useState(false);
  const webcamRef = useRef(null);

  const handleStartRecording = async () => {
    setIsRecording(true);

    const intervalId = setInterval(async () => {
      try {
        const videoData = webcamRef.current.getVideoElementsCaptured();
        const processedVideo = await ffmpeg.encodeVideo(videoData, {
          outputOptions: [
            '-c:v', 'libx264', // Video codec
            '-vf', 'drawtext=fontfile=Arial.ttf:text=\'%{pts}\':fontsize=24:color=white@0.8:x=(w-text_w)/2:y=(h-text_h)/2', // Timestamp overlay
            '-crf', '23', // Adjust quality
          ],
        });

        const response = await axios.post('/start', processedVideo, {
          headers: { 'Content-Type': 'video/mp4' },
        });

        onVideoSaved(response.data); // Pass saved video data (if applicable)
      } catch (error) {
        console.error('Error during recording:', error);
      }
    }, 1000); // Adjust capture interval as needed

    return () => clearInterval(intervalId);
  };

  const handleStopRecording = () => {
    setIsRecording(false);
  };

  return (
    <div>
      <Webcam ref={webcamRef} />
      <button onClick={isRecording ? handleStopRecording : handleStartRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
};

export default VideoRecorder;
