import * as React from 'react';
import { Stack, Button } from '@mui/material';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import axiosInstance from '../../axiosConfig'; // Import the configured Axios instance

export default function RecordingButtons({username, material, speed}) {

  const [loading, setLoading] = React.useState(false);
  const [recording, setRecording] = React.useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = React.useState(false);


  const handleClick = async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      if (recording) {
        // Handle stop recording logic
        const response = await axiosInstance.get('/stop');
        console.log('Stop recording', response.data);
        setDeleteLastPossible(true);
      } else {
        // Handle start recording logic
        const response = await axiosInstance.post('/start', {
            username,
            material,
            speed,
          }
        );
        console.log('Start recording', response.data);
        setDeleteLastPossible(false);
      }
      // Toggle recording state after API call
      setRecording((prevRecording) => !prevRecording);
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  };

  const handleDeleteLastRecording = async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      // Handle delete last recording logic
      const response = await axiosInstance.get('/delete_last');
      console.log('Delete last recording', response.data);
      setDeleteLastPossible(false);
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
    } finally {
      setLoading(false); // Reset loading state after API call is completed
    }
  };

  return (
    <Stack direction="row" spacing={2}>
      <Button
        onClick={handleClick}
        variant="contained"
        startIcon={recording ? <RadioButtonCheckedIcon sx={{ color: 'red' }} /> : null}
        disabled={loading || speed == undefined || material == undefined}
      >
        {recording ? 'Stop Recording' : 'Start Recording'}
      </Button>
      {isDeleteLastPossible && (
        <Button
          onClick={handleDeleteLastRecording}
          variant="contained"
          disabled={loading}
          startIcon={<DeleteOutlineIcon />}
        >
          Delete Last Recording
        </Button>
      )}
    </Stack>
  );
}
