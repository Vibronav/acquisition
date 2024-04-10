import Button from '@mui/material/Button';
import React, { useRef } from 'react';
import Webcam from 'react-webcam';


const WebcamStreamCapture = () => {
    const webcamRef = React.useRef(null);
    const mediaRecorderRef = React.useRef(null);
    const [capturing, setCapturing] = React.useState(false);
    const [recordedChunks, setRecordedChunks] = React.useState([]);
  
    const handleStartCaptureClick = React.useCallback(() => {
      setCapturing(true);
      mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
        mimeType: "video/webm"
      });
      mediaRecorderRef.current.addEventListener(
        "dataavailable",
        handleDataAvailable
      );
      mediaRecorderRef.current.start();
    }, [webcamRef, setCapturing, mediaRecorderRef]);
  
    const handleDataAvailable = React.useCallback(
      ({ data }) => {
        if (data.size > 0) {
          setRecordedChunks((prev) => prev.concat(data));
        }
      },
      [setRecordedChunks]
    );
  
    const handleStopCaptureClick = React.useCallback(() => {
      mediaRecorderRef.current.stop();
      setCapturing(false);
    }, [mediaRecorderRef, webcamRef, setCapturing]);
  
    const handleDownload = React.useCallback(() => {
      if (recordedChunks.length) {
        const blob = new Blob(recordedChunks, {
          type: "video/webm"
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        document.body.appendChild(a);
        a.style = "display: none";
        a.href = url;
        a.download = "react-webcam-stream-capture.webm";
        a.click();
        window.URL.revokeObjectURL(url);
        setRecordedChunks([]);
      }
    }, [recordedChunks]);
  
    return (
        <div style={{ display: 'grid', gridTemplateRows: 'auto 1fr', gap: 16 }}>
          <Webcam audio={false} ref={webcamRef} />
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            {capturing ? (
              <Button onClick={handleStopCaptureClick}>Stop Capture</Button>
            ) : (
              <Button onClick={handleStartCaptureClick}>Start Capture</Button>
            )}
            {recordedChunks.length > 0 && (
              <Button onClick={handleDownload}>Download</Button>
            )}
          </div>
        </div>
      );
  };

export default WebcamStreamCapture;

