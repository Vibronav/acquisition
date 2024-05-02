import React, { useEffect, useState } from 'react';
import { Container, Select, TextField, Stack, InputLabel, MenuItem, FormControl } from '@mui/material';

import VideoAudioSelect from '../components/VideoAudioSelect.jsx'
import RecordingButtons from '../components/RecordingButtons.jsx';
import WebcamRenderer from '../components/WebcamRenderer.jsx';
import { selectStyles, stackStyles, formControlStyles } from './../themes';


const Acquisition = ({ setIsConfigChange, isConfigChange }) => {
    // State variables
    
    const [materials, setMaterials] = useState([]); // Materials state
    const [speeds, setSpeeds] = useState([]); // Speeds state
    const [selectedVideoDevices, setSelectedVideoDevices] = useState([]); // Selected video devices state
    const [selectedAudioDevice, setSelectedAudioDevice] = useState(''); // Selected audio device state
    const [videoDevices, setVideoDevices] = useState([]); // Video devices state
    const [audioDevices, setAudioDevices] = useState([]); // Audio devices state

    const proxy = "http://127.0.0.1:5000/api"; // Proxy URL for API requests

    useEffect(() => {
        // Fetch materials and speeds data from API
        const fetchData = async () => {
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
            }
        };

        fetchData();
    }, []);



    return (
        <div>
                <Stack sx={stackStyles}>

                    {/* Video and audio selection component */}
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

                    {/* Stack for username, material, and speed selection */}
                    <Stack
                        sx={stackStyles} direction="row">
                        <FormControl
                            sx={formControlStyles} >
                            <InputLabel >Username</InputLabel>
                            <TextField id="username" labelId="usernameLabel" />
                        </FormControl>

                        <FormControl
                            sx={formControlStyles} >
                            <InputLabel >Material</InputLabel>
                            <Select
                                sx={selectStyles}
                                labelId="materialSelect"
                                label="Material"
                                id="material"

                            >
                                {/* Render material options */}
                                {materials.map((material) => (
                                    <MenuItem key={material} value={material}>
                                        {material}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <FormControl
                            sx={formControlStyles} >
                            <InputLabel >Speed</InputLabel>
                            <Select
                                sx={selectStyles}
                                labelId="materialSelect"
                                label="Speed"
                                id="speed"
                            >
                                {/* Render speed options */}
                                {speeds.map((speeds) => (
                                    <MenuItem key={speeds} value={speeds}>
                                        {speeds}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                    </Stack>

                    {/* Stack for video recording controls */}
                    <Stack
                        sx={stackStyles} mt={3} spacing={2} >

                        <RecordingButtons />
                        {/* Component for rendering webcams */}
                        <WebcamRenderer selectedVideoDevices={selectedVideoDevices} videoDevices={videoDevices} />
                    </Stack>

                </Stack>
 

    </div >
  );
}

export default Acquisition;
