import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';import DownloadIcon from '@mui/icons-material/Download';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import { Button, Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useIntl } from 'react-intl';
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
  videoDevices: PropTypes.array.isRequired,
  audioFiles: PropTypes.array.isRequired,
  setAudioFiles: PropTypes.func.isRequired,
  setRecordingStatus: PropTypes.string.isRequired
};

export default function RecordingButtons({ 
  username, 
  material, 
  speed, 
  measurementCounter, 
  setMeasurementCounter,
  selectedVideoDevices,
  videoDevices, 
  setAudioFiles,
  setRecordingStatus
 }) {
  
  const intl = useIntl();

  const webcamRef = useRef(null);
  const mediaRecordedRef = useRef(null);
  const downloadRef = useRef(null);
  const [recordedChunks, setRecordedChunks] = useState([]);

  const handleDataAvailable = useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks(prev => prev.concat(data));
      }
    },
    [setRecordedChunks]
  );

  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = useState(false);
  const [debugMessage, setDebugMessage] = useState("");

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
      
      let date = new Date();
      let formattedDate = date.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }).replace(/, /g, '_').replace(/:/g, '-');
      const filename = username + '_' + material+ '_' +speed + '_' + formattedDate + '.mp4'

      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style = 'display: none';
      a.href = url;
      a.download = filename;
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      setDebugMessage(intl.formatMessage({ id: 'recordingDownloaded' }));
    }
  };

  const handleRecording = useCallback(async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      if (recording) {
        const response = await axiosInstance.get('/stop');
        const filenames = response.data.map(file => file.filename);
        setDebugMessage(intl.formatMessage({ id: 'recordingSaved' }) + filenames.join(', '));
        setMeasurementCounter(measurementCounter + 1);
        setDeleteLastPossible(true);
        setAudioFiles(response.data);
        setRecordingStatus("stop");

      } else {
        setDebugMessage(intl.formatMessage({ id: 'connectingToRaspberry' }));
        await axiosInstance.post('/start', {
          username,
          material,
          speed,
        });
        setDebugMessage(intl.formatMessage({ id: 'recordingStarted' }));
        setDeleteLastPossible(false);
        setRecordingStatus("start");
      }
      setRecording(prevRecording => !prevRecording);
    } catch (error) {
      setDebugMessage(intl.formatMessage({ id: 'recordingConnectFailed' }) + error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }, [recording, measurementCounter, username, material, speed, setMeasurementCounter, setAudioFiles]);

  const handleDeleteLastRecording = useCallback(async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      const response = await axiosInstance.get('/delete_last');
      setDebugMessage(intl.formatMessage({ id: 'recordingDeleteSuccess' }) + response.data);
      setMeasurementCounter(measurementCounter - 1 >= 0 ? measurementCounter - 1 : 0);
      setDeleteLastPossible(false);
      setRecordedChunks([]);
      setRecordingStatus("delete");
    } catch (error) {
      setDebugMessage(intl.formatMessage({ id: 'recordingDeleteFailed' }) + error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }, [measurementCounter, setMeasurementCounter]);

  useEffect(() => {
    const handleKeyPress = (event) => {
      if (loading || speed == undefined || material == undefined || speed == null || material == null) {
        return;
      }
      if (event.ctrlKey && event.shiftKey && event.key === 'R') {
        handleRecording();
      } else if (event.ctrlKey && event.shiftKey && event.key === 'D') {
        handleDeleteLastRecording();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => {
      window.removeEventListener('keydown', handleKeyPress);
    };
  }, [handleRecording, handleDeleteLastRecording]);

  return (
    <Stack spacing={2}>
      <Stack direction="row" spacing={2}>
        <Button
          onClick={handleRecording}
          variant="contained"
          startIcon={recording ? <RadioButtonCheckedIcon sx={{ color: 'red' }} /> : null}
          disabled={loading || speed == undefined || material == undefined || speed == null || material == null}
        >
          {recording ? intl.formatMessage({ id: 'stopRecording' }) : intl.formatMessage({ id: 'startRecording' })}
        </Button>
        {isDeleteLastPossible && (
          <Button
            onClick={handleDeleteLastRecording}
            variant="contained"
            disabled={loading || speed == undefined || material == undefined || speed == null || material == null}
            startIcon={<DeleteOutlineIcon />}
          >
            {intl.formatMessage({ id: 'deleteRecording' })}
          </Button>
        )}
        {recordedChunks.length > 0 && (
          <Button
            onClick={handleDownloadingRecording}
            variant="contained"
            ref={downloadRef}
            disabled={loading || speed == undefined || material == undefined || speed == null || material == null}
            startIcon={<DownloadIcon />}
          >
            {intl.formatMessage({ id: 'downloadRecording' })}
          </Button>
        )}
      </Stack>
      <Typography>{debugMessage}</Typography>
      <WebcamRenderer selectedVideoDevices={selectedVideoDevices} videoDevices={videoDevices} webcamRef={webcamRef}/>
    </Stack>
  );
}
