import * as React from 'react';
import { Stack, Button, Typography } from '@mui/material';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import axiosInstance from '../../axiosConfig'; // Import the configured Axios instance
import PropTypes from 'prop-types';




export default function RecordingButtons({ username, material, speed, measurementCounter, setMeasurementCounter }) {

  const [loading, setLoading] = React.useState(false);
  const [recording, setRecording] = React.useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = React.useState(false);
  const [debugMessage, setDebugMessage] = React.useState("");

  const handleClick = React.useCallback(async () => {
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
    } catch (error) {
      setDebugMessage('❌ There was a problem with the delete operation: ' + error);
      console.log('There was a problem with the delete operation:', error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  }, [measurementCounter, setMeasurementCounter]);

  React.useEffect(() => {
    const handleKeyPress = (event) => {
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
          disabled={loading || speed === undefined || material === undefined}
        >
          {recording ? 'Stop Recording' : 'Start Recording'}
        </Button>
        {isDeleteLastPossible && (
          <Button
            onClick={handleDeleteLastRecording}
            variant="contained"
            disabled={loading || speed == null || material == null}
            startIcon={<DeleteOutlineIcon />}
          >
            Delete Last Recording
          </Button>
        )}

      </Stack>
      <Typography>{debugMessage}</Typography>
    </Stack>
  );
}

RecordingButtons.propTypes = {
  username: PropTypes.string.isRequired,
  material: PropTypes.string,
  speed: PropTypes.string,
  measurementCounter: PropTypes.number.isRequired,
  setMeasurementCounter: PropTypes.func.isRequired,
};
