import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';import DownloadIcon from '@mui/icons-material/Download';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import { Button, Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useIntl } from 'react-intl';
import RecordRTC from 'recordrtc';
import axiosInstance from '../../axiosConfig'; // Import the configured Axios instance
import WebcamRenderer from './WebcamRenderer';
import AudioVisualizer from './AudioVisualizer';
import AudioStream from './Audio_Vis.jsx';

RecordingButtons.propTypes = {
  username: PropTypes.string.isRequired,
  material: PropTypes.string,
  speed: PropTypes.string,
  positionType: PropTypes.string.isRequired,
  P1: PropTypes.string.isRequired,
  P2: PropTypes.string.isRequired,
  P3: PropTypes.string.isRequired,
  numIterations: PropTypes.number.isRequired,
  isCamera: PropTypes.bool.isRequired,
  measurementCounter: PropTypes.number.isRequired,
  setMeasurementCounter: PropTypes.func.isRequired,
  isRecordingStarted: PropTypes.func.isRequired,
  selectedVideoDevices: PropTypes.array.isRequired,
  videoDevices: PropTypes.array.isRequired,
  audioFiles: PropTypes.array.isRequired,
  setAudioFiles: PropTypes.func.isRequired,
  setRecordingStatus: PropTypes.string.isRequired,
  localDir: PropTypes.string.isRequired
};

export default function RecordingButtons({ 
  username, 
  material, 
  speed, 
  positionType,
  P1,
  P2,
  P3,
  numIterations,
  measurementCounter, 
  setMeasurementCounter,
  selectedVideoDevices,
  videoDevices, 
  setAudioFiles,
  setRecordingStatus,
  localDir
 }) {
  
  const intl = useIntl();

  const webcamRef = useRef(null);
  const mediaRecordersRef = useRef([]);
  const [downloadRefs, setDownloadRefs] = useState([]); // State to keep track of download references (optional)
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [cameraIndexes, setCameraIndexes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = useState(false);
  const [debugMessage, setDebugMessage] = useState("");
  
  const handleDataAvailable = useCallback(
    (recorder, { data }, cameraIndex) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => [
          ...prev,
          { recorder, data, cameraIndex }, // Store data with cameraIndex
        ]);
      }
    },
    [setRecordedChunks]
  );
  
  const startRecording = async () => {
    try {
      const recorders = await Promise.all(
        cameraIndexes.map(async (index) => {
          const videoDevice = videoDevices[index]; // Find the device based on the index
          if (!videoDevice){
            console.log("Video device not found. Camera Index: " + index)
            return null;
          } 
  
          // Get media stream for the specified device
          const stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: videoDevice.deviceId } },
            audio: true, // Include audio if needed; adjust as required
          });
  
          // Create a new recorder for the current stream
          const recorder = new RecordRTC(stream, {
            mimeType: 'video/webm',
          });
  
          // Start recording and handle the data
          recorder.startRecording();
          recorder.ondataavailable = (data) => handleDataAvailable(recorder, { data }, index);
  
          // Add the recorder and stream to the ref array for later use
          mediaRecordersRef.current.push({ recorder, stream });
          return { recorder, stream };
        })
      );
  
      // Filter out any failed stream initializations
      const activeRecorders = recorders.filter(Boolean);
      mediaRecordersRef.current = activeRecorders;
    } catch (error) {
      console.error('Error starting multiple recordings:', error);
      setDebugMessage(`Error starting recordings: ${error.message}`);
    }
  };
  
  // Stop all recordings simultaneously
  const stopRecording = () => {
    // Check if mediaRecordersRef.current is defined and has recorders to stop
    if (mediaRecordersRef.current && mediaRecordersRef.current.length > 0) {
      mediaRecordersRef.current.forEach(({ recorder, stream }) => {
        recorder.stopRecording(() => {
          const blob = recorder.getBlob();
          handleDataAvailable(recorder, { data: blob }); // Call handleDataAvailable with final blob
        });
        // Stop all tracks in the stream
        stream.getTracks().forEach((track) => track.stop());
      });

      // Clear the recorder references after stopping to reset the state
      mediaRecordersRef.current = [];
    } else {
      console.warn('No recordings to stop or recorders were not initialized.');
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
    if (recordedChunks && recordedChunks.length > 0) {

        setDeleteLastPossible(false);

        let index = 0; // Initialize counter
        
        // Create an array to hold the promises for sending data
        const uploadPromises = recordedChunks.map(async ({ data, cameraIndex }) => {
            const blob = new Blob([data], { type: 'video/webm' });

            const date = new Date();
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
            const day = String(date.getDate()).padStart(2, '0');
            const hour = String(date.getHours()).padStart(2, '0');
            const minute = String(date.getMinutes()).padStart(2, '0');
            const second = String(date.getSeconds()).padStart(2, '0');

            const formattedDate = `${year}-${month}-${day}_${hour}.${minute}.${second}`;
            const filename = `${username}_${material}_${speed}_camera${cameraIndex || index}_${formattedDate}.webm`;

            // Increment index if cameraIndex is not defined
            if (cameraIndex === undefined) {
                index++;
            }

            // Convert the blob to base64 for sending
            const reader = new FileReader();
            return new Promise((resolve, reject) => {
                reader.onloadend = async () => {
                    const base64data = reader.result.split(',')[1]; // Get base64 string
                    try {
                        const response = await axiosInstance.post('/save_video', {
                            filename: filename,
                            local_dir: localDir,
                            data: base64data,
                        });

                        resolve(response.data);
                    } catch (error) {
                        console.error('Error uploading video:', error);
                        reject(error);
                    }
                };
                reader.readAsDataURL(blob); // Read the blob as a data URL
            });
        });

        // Wait for all uploads to complete
        try {
            const results = await Promise.all(uploadPromises);
            console.log("Uploaded videos:", results);
            setDebugMessage(intl.formatMessage({ id: 'recordingUploaded' }) + results[0].filename  );
        } catch (error) {
            console.error('Error during upload:', error);
        }
    } else {
        console.log("Error with recorded chunks");
    }
};

const handleRecording = useCallback(async () => {
  setLoading(true); // Set loading state while API call is in progress
  setRecordingStatus("start");
  
  for (let i = 1; i <= numIterations; i++) {
    try {
      setDebugMessage(intl.formatMessage({ id: 'connectingToRaspberry' }));

      if (isDeleteLastPossible) {
        await handleDownloadingRecording();
      }

      setDeleteLastPossible(false);

      setCameraIndexes(
        selectedVideoDevices
          .map((selectedLabel) => videoDevices.findIndex((device) => device.label === selectedLabel))
          .filter((index) => index !== -1)
      );
      setRecordedChunks([]);
      setDebugMessage(i + ': ' + intl.formatMessage({ id: 'recordingStarted' }));
      console.log("REC");
      
      // Await the axios post request to ensure it completes before moving on
      const response = await axiosInstance.post('/start_dobot', {
        username,
        material,
        speed,
        positionType,
        P1,
        P2,
        P3
      });

      // Optionally handle the response from the server
      console.log("Start Dobot response:", response.data);

      // After start_dobot call is finished - stop also camera recording
      const stopResponse = await axiosInstance.get('/stop');
      const filenames = stopResponse.data.map(file => file.filename);
      console.log("FILENAMES:", filenames);
      setDebugMessage(i + ': ' + intl.formatMessage({ id: 'recordedSuccesfully' }) + filenames.join(', '));
      
    } catch (error) {
      setDebugMessage(intl.formatMessage({ id: 'recordingConnectFailed' }) + error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }
  
  setRecordingStatus("stop");
  setDeleteLastPossible(true);
}, [setRecordingStatus, username, material, speed, isDeleteLastPossible, selectedVideoDevices, videoDevices]);


  // const handleRecording = useCallback(async () => {
  //   setLoading(true); // Set loading state while API call is in progress
  //   setRecordingStatus("start");
  //   for (let i = 1; i <= numIterations; i++) {
  //     try {
        
  //         setDebugMessage(intl.formatMessage({ id: 'connectingToRaspberry' }));
          

  //         if(isDeleteLastPossible){
  //           await handleDownloadingRecording();
  //         }

  //         setDeleteLastPossible(false);

  //         setCameraIndexes(
  //           selectedVideoDevices
  //             .map((selectedLabel) => videoDevices.findIndex((device) => device.label === selectedLabel))
  //             .filter((index) => index !== -1)
  //         );
  //         setRecordedChunks([]);
  //         setDebugMessage(i +': '+intl.formatMessage({ id: 'recordingStarted' }));
  //         console.log("REC")
  //         // synchronous call, will execute dobot acquisition movements
  //         axiosInstance.post('/start_dobot', {
  //           username,
  //           material,
  //           speed,
  //           positionType,
  //           P1,
  //           P2,
  //           P3
  //         });
          

  //         // // after start_dobot call is finished - stop also camera recording
  //         // const response = axiosInstance.get('/stop');
  //         // const filenames = response.data.map(file => file.filename);
  //         // console.log("FILENAMES :", filenames)
  //         // console.log("RESPONSE :",response)
  //         // setDebugMessage(i +': ' + intl.formatMessage({ id: 'recordedSuccesfully' }) + filenames.join(', '));
  //         // setMeasurementCounter(measurementCounter + 1);
  //         // setAudioFiles(response.data);
          
        
  //     } catch (error) {
  //       setDebugMessage(intl.formatMessage({ id: 'recordingConnectFailed' }) + error);
  //     } finally {
  //       setLoading(false); // Reset loading state after API call is completed
  //     }

      
  //   }
  //   setRecordingStatus("stop");
  //   setDeleteLastPossible(true);

  // }, [recording, measurementCounter, username, material, speed, setMeasurementCounter, setAudioFiles]);

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
      {/* <AudioStream></AudioStream> */}
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
        {isDeleteLastPossible && recordedChunks && recordedChunks.length > 0 && (
          <Button
            onClick={handleDownloadingRecording}
            variant="contained"
            ref={downloadRefs}
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