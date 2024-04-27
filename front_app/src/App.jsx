import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Container, Select, TextField, Stack, InputLabel, MenuItem, Typography, CssBaseline } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import ThemeSwitchButton from './ThemeSwitchButton.jsx'
import VideoAudioSelect from './VideoAudioSelect.jsx'
import RecordingButtons from './RecordingButtons.jsx';
import Webcam from 'react-webcam';
import './App.css'; // Import global CSS file

const App = () => {
  const [light, setLight] = useState(false);
  const [materials, setMaterials] = useState([]);
  const [speeds, setSpeeds] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedVideoDevices, setSelectedVideoDevices] = useState([]);
  const [selectedAudioDevice, setSelectedAudioDevice] = useState('');
  const [videoDevices, setVideoDevices] = useState([]);
  const [audioDevices, setAudioDevices] = useState([]);

  const proxy = "http://127.0.0.1:5000/api";

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(proxy + "/parse_config");
        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.status}`);
        }
        const data = await response.json();
        setMaterials(data.materials);
        setSpeeds(data.speeds)
      } catch (error) {
        console.error('Error fetching materials:', error);
        setError(error.message); // Set a user-friendly error message
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

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

  const renderWebcams = () => {
    switch (selectedVideoDevices.length) {
      case 0:
        return (
          <div style={{ width: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', height: 430, border: '2px dashed black', borderRadius: 10 }}>
            <p style={{ textAlign: 'center', fontSize: 24 }}>Select video device</p>
          </div>
        );
        case 1:
          // Find the device object in videoDevices array with matching label
          const device = videoDevices.find(device => device.label === selectedVideoDevices[0]);
          
          return (
            <div style={{ display: 'flex', alignItems: 'center', gap: "20px" }}>
              {device && (
                <Stack>
                  <Typography>{device.label}</Typography>
                  <Webcam
                    videoConstraints={{ deviceId: device.deviceId }}
                    style={{ borderRadius: 10, width: '100%', height: 'auto' }}
                  />
                </Stack>
              )}
              <div style={{ width: '50%', height: 450, border: '2px dashed black', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 10 }}>
                <p style={{ textAlign: 'center', fontSize: 24 }}>Select video device</p>
              </div>
            </div>
          );
      default:
        return (
          <div style={{ overflowX: 'auto', whiteSpace: 'nowrap', display: "flex", gap: "20px" }}>
            {selectedVideoDevices.map(label => {
              // Find the device object in videoDevices array with matching label
              const device = videoDevices.find(device => device.label === label);

              // Check if device is found
              if (device) {
                return (
                  <Stack key={device.deviceId}>
                    <Typography>{device.label}</Typography>
                    <Webcam
                      videoConstraints={{ deviceId: device.deviceId }}
                      style={{ width: '100%', height: 'auto', borderRadius: 10 }}
                    />
                  </Stack>
                );
              } else {
                return null; // Handle case when device is not found
              }
            })}
          </div>
        );

    }
  };


  return (
    <div>
      <ThemeProvider theme={light ? lightTheme : darkTheme}>
        <CssBaseline />
        <Container maxWidth="lg" style={{ marginTop: '20px' }}>
          <Stack spacing={5}>
            <ThemeSwitchButton currentTheme={light} onChange={toggleTheme} />

            <VideoAudioSelect
              selectedVideoDevices={selectedVideoDevices}
              setSelectedVideoDevices={setSelectedVideoDevices}
              selectedAudioDevice={selectedAudioDevice}
              setSelectedAudioDevice={setSelectedAudioDevice}
              videoDevices={videoDevices}
              setVideoDevices={setVideoDevices}
              audioDevices={audioDevices}
              setAudioDevices={setAudioDevices}
            />

            <Stack direction="row">
              <Stack className="username">
                <InputLabel variant="usernameLabel">Username</InputLabel>
                <TextField id="username" variant="outlined" className="fullWidth" labelId="usernameLabel" />
              </Stack>
              <Stack className="material">
                <InputLabel variant="standard">Material</InputLabel>
                <Select
                  labelId="materialSelect"
                  className="fullWidth"
                  label="Material"
                  id="material"

                >
                  {materials.map((material) => (
                    <MenuItem key={material} value={material}>
                      {material}
                    </MenuItem>
                  ))}
                </Select>
              </Stack>
              <Stack className="speed">
                <InputLabel variant="standard">Speed</InputLabel>
                <Select
                  labelId="materialSelect"
                  className="fullWidth"
                  label="Speed"
                  id="speed"
                >
                  {speeds.map((speeds) => (
                    <MenuItem key={speeds} value={speeds}>
                      {speeds}
                    </MenuItem>
                  ))}
                </Select>
              </Stack>
            </Stack>

            <Stack className="video" spacing={4}>
              <Stack direction="row" id="controls">
                <RecordingButtons />
              </Stack>
              {/* Render Webcams based on selected video devices */}
              {renderWebcams()}
            </Stack>

          </Stack>
        </Container>
      </ThemeProvider>
    </div>
  );
}

export default App;
