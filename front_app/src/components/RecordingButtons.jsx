import { createFFmpeg, fetchFile } from '@ffmpeg/ffmpeg';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import DownloadIcon from '@mui/icons-material/Download';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import { Button, Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import * as React from 'react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { FormattedMessage } from 'react-intl';
import RecordRTC from 'recordrtc';
import axiosInstance from '../../axiosConfig'; // Import the configured Axios instance
import WebcamRenderer from './WebcamRenderer';

RecordingButtons.propTypes = {
  username: PropTypes.string.isRequired,
  material: PropTypes.string,
  speed: PropTypes.string,
  isCamera: PropTypes.bool.isRequired,
  measurementCounter: PropTypes.number.isRequired,
  setMeasurementCounter: PropTypes.func.isRequired,
  isRecordingStarted: PropTypes.func.isRequired,
  selectedVideoDevices: PropTypes.array.isRequired,
  videoDevices: PropTypes.array.isRequired
};

//we use old ffmpeg because the new ones does not work 
const ffmpeg = createFFmpeg();

export default function RecordingButtons({ username, material, speed, measurementCounter, setMeasurementCounter
  ,selectedVideoDevices,videoDevices
 }) {

  //recording values
  const webcamRef = useRef(null);
  const mediaRecordedRef = useRef(null);
  const downloadRef = useRef(null);
  const [recordedChunks, setRecordedChunks] = useState([]);

  const handleDataAvailable = useCallback(
    ({data}) => {
      if (data.size > 0){
        setRecordedChunks(prev => prev.concat(data))
      }
    },[setRecordedChunks]
  );

  const [loading, setLoading] = React.useState(false);
  const [recording, setRecording] = React.useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = React.useState(false);
  const [debugMessage, setDebugMessage] = React.useState("");

  const startRecording = () => {
    if (webcamRef.current && webcamRef.current.stream) {
      
      mediaRecordedRef.current = new RecordRTC(webcamRef.current.stream, {
        mimeType: 'video/webm'
      });
      mediaRecordedRef.current.startRecording();
      mediaRecordedRef.current.ondataavailable = handleDataAvailable;
    }
  };

  const stopRecording = () => {
    if (mediaRecordedRef.current) {
      mediaRecordedRef.current.stopRecording(() => {
        const blob = mediaRecordedRef.current.getBlob();
        setRecordedChunks([blob]);
      });
    }
  };

  useEffect(() => {
    if (recording) {
      startRecording();
    } else {
      stopRecording();
    }
  }, [recording]);  

  const handleDownloadingRecording = async () => {
    if (recordedChunks.length > 0) {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      const url = URL.createObjectURL(blob);
      
      if (!ffmpeg.isLoaded()){
        await ffmpeg.load({
          env: {
            USE_SDL: false
          },
        });
      }
      
      ffmpeg.FS('writeFile', 'recording.webm', await fetchFile(url));
      await ffmpeg.run('-i', 'recording.webm', 'recording.mp4');
      const mp4Data = ffmpeg.FS('readFile', 'recording.mp4');
      const mp4Blob = new Blob([mp4Data.buffer], { type: 'video/mp4' });
      const mp4Url = URL.createObjectURL(mp4Blob);

      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style = 'display: none';
      a.href = mp4Url;
      a.download = 'recording.mp4';
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(mp4Url);

      setDebugMessage("Recording downloaded.");
    }
  };

  const handleClick = React.useCallback(async () =>  {
    setLoading(true); // Set loading state while API call is in progress
    try {
      if (recording) {
        // Handle stop recording logic
        const response = await axiosInstance.get('/stop');
        setDebugMessage("Recording saved: "+ response.data)
        console.log('Stop recording', response.data);
        setMeasurementCounter(measurementCounter + 1);
        setDeleteLastPossible(true);
      } else {
        // Handle start recording logic
        setDebugMessage("Connecting to RaspberryPi with SSH...");
        const response = await axiosInstance.post('/start', {
          username,
          material,
          speed,
        });
        setDebugMessage("Recording started.");
        console.log("Recording started.", response.data);
        setDeleteLastPossible(false);
      }
      // Toggle recording state after API call
      setRecording((prevRecording) => !prevRecording);
    } catch (error) {
      setDebugMessage('❌ Connection to raspberrypi failed. ' + error);
      console.log("Connection to raspberrypi failed.", error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }, [recording, measurementCounter, username, material, speed, setMeasurementCounter]);

  const handleDeleteLastRecording = React.useCallback(async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      // Handle delete last recording logic
      const response = await axiosInstance.get('/delete_last');
      setDebugMessage('Last recording deleted succesfully. ' + response.data);
      setMeasurementCounter(measurementCounter - 1 >= 0 ? measurementCounter - 1 : 0);
      setDeleteLastPossible(false);
      setRecordedChunks([])
    } catch (error) {
      setDebugMessage('❌ There was a problem with the delete operation: ' + error);
      console.log('There was a problem with the delete operation:', error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }, [measurementCounter, setMeasurementCounter]);

  React.useEffect(() => {
    const handleKeyPress = (event) => {
      if(loading 
        || speed == undefined 
        || material == undefined
        || speed == null 
        || material == null){
          return
      }
      if (event.ctrlKey && event.shiftKey && event.key === 'R') {
        handleClick();
      } else if (event.ctrlKey && event.shiftKey && event.key === 'D') {
        handleDeleteLastRecording();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleClick, handleDeleteLastRecording]);

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={2}>
        <Button
          onClick={handleClick}
          variant="contained"
          startIcon={recording ? <RadioButtonCheckedIcon sx={{ color: 'red' }} /> : null}
          disabled={loading 
            || speed == undefined 
            || material == undefined
            || speed == null 
            || material == null}
        >
          {recording ? <FormattedMessage id="stopRecording"/> : <FormattedMessage id="startRecording"/>}
        </Button>
        {isDeleteLastPossible && (
          <Button
            onClick={handleDeleteLastRecording}
            variant="contained"
            disabled={loading 
              || speed == undefined 
              || material == undefined
              || speed == null 
              || material == null}
            startIcon={<DeleteOutlineIcon />}
          >
            <FormattedMessage id="deleteRecording"/>
          </Button>
        )}
        {
          recordedChunks.length > 0 && (
            <Button
              onClick={handleDownloadingRecording}
              variant="contained"
              ref={downloadRef}
              disabled={loading 
                || speed == undefined 
                || material == undefined
                || speed == null 
                || material == null}
              startIcon={<DownloadIcon />}
            >
              <FormattedMessage id="downloadRecording"/>
            </Button>
          )
        }

      </Stack>
      <Typography>{debugMessage}</Typography>
      <WebcamRenderer selectedVideoDevices={selectedVideoDevices} videoDevices={videoDevices} webcamRef={webcamRef}/>
    </Stack>
  );
}
