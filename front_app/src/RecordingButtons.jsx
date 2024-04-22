import * as React from 'react';
import { Stack, Button } from '@mui/material';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';

export default function RecordingButtons() {
  const [loading, setLoading] = React.useState(false);
  const [recording, setRecording] = React.useState(false);
  const [isDeleteLastPossible, setDeleteLastPossible] = React.useState(false);

  const handleClick = async () => {
    setLoading(true); // Set loading state while API call is in progress
    try {
      if (recording) {
        // Handle stop recording logic
        // Simulate API call delay
        //await new Promise((resolve) => setTimeout(resolve, 1000));
        console.log('Stop recording');
        setDeleteLastPossible(true);
      } else {
        // Handle start recording logic
        // Simulate API call delay
        //await new Promise((resolve) => setTimeout(resolve, 1000));
        console.log('Start recording');
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
      // Simulate API call delay
      //await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log('Delete last recording');
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
        size="small"
        startIcon={recording ? <RadioButtonCheckedIcon sx={{ color: 'red' }} /> : null}
        disabled={loading}
      >
        {recording ? 'Stop Recording' : 'Start Recording'}
      </Button>
      {isDeleteLastPossible && (
        <Button
          onClick={handleDeleteLastRecording}
          variant="contained"
          size="small"
          disabled={loading}
          startIcon={<DeleteOutlineIcon/>}
        >
          Delete Last Recording
        </Button>
      )}
    </Stack>
  );
}
