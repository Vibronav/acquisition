import * as React from 'react';
import { Fragment } from 'react';
import { Container, Grid, Select, TextField, Typography, Button, CssBaseline, Stack, InputLabel } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ThemeSwitchButton from './ThemeSwitchButton.jsx'
import VideoAudioSelect from './VideoAudioSelect.jsx'
import RecordingButtons from './RecordingButtons.jsx';
import Webcam from 'react-webcam';
import './App.css'; // Import global CSS file

const App = () => {
  const [light, setLight] = React.useState(false);
  const [recording, setRecording] = React.useState(false); // State to track recording status

  const toggleTheme = () => {
    setLight((prevTheme) => !prevTheme); // Toggle the theme based on the current state
  };

  const darkTheme = createTheme({
    palette: {
      type: 'dark',
      background: {
        default: "#404045",
        paper: "#424242"
      },
      primary: {
        main: '#568166',
        contrastText: "#fff"
      },
      secondary: {
        main: '#fb8c00',
        contrastText: "rgba(0, 0, 0, 0.87)"
      },
      text: {
        primary: '#fff',
        secondary: "rgba(255, 255, 255, 0.7)",
        disabled: "rgba(255, 255, 255, 0.5)",
        hint: "rgba(255, 255, 255, 0.5)"
      },
      divider: "rgba(255, 255, 255, 0.12)",


    },



  });

  const lightTheme = createTheme({
    palette: {
      type: 'light',
      primary: {
        main: '#568166',
      },
      secondary: {
        main: '#fb8c00',
      },
    },
  });


  return (
    <React.Fragment className="content-wrapper">
      <ThemeProvider theme={light ? lightTheme : darkTheme}>
        <CssBaseline />
        <Container maxWidth="lg" >
          <Stack spacing={5}>
            <ThemeSwitchButton currentTheme={light} onChange={toggleTheme} />
            
            <VideoAudioSelect />
            
            <Stack direction="row">
              <Stack className="username">
                <InputLabel variant="usernameLabel">Username</InputLabel>
                <TextField id="username" variant="outlined" className="fullWidth" labelId="usernameLabel" />
              </Stack>
              <Stack className="material">
                <InputLabel variant="materialSelect">Material</InputLabel>
                <Select
                  labelId="materialSelect"
                  className="fullWidth"
                  label="Material"
                  id="material"
                ></Select>
              </Stack>
              <Stack className="speed">
                <InputLabel variant="speedSelect">Speed</InputLabel>
                <Select
                  labelId="materialSelect"
                  className="fullWidth"
                  label="Speed"
                  id="speed"></Select>
              </Stack>
            </Stack>

            <Stack className="video" spacing={4}>
              <Stack direction="row" id="controls">
                <RecordingButtons />
              </Stack>
              <Fragment>
                <Webcam audio={false} />
              </Fragment>
            </Stack>

          </Stack>
        </Container>
      </ThemeProvider>
    </React.Fragment>
  );
}

export default App;
