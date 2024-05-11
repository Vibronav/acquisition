import React, { useEffect, useState } from 'react';
import { Container, Select, Typography, Stack, InputLabel, MenuItem, FormControl } from '@mui/material';

import VideoAudioSelect from '../components/VideoAudioSelect.jsx'
import RecordingButtons from '../components/RecordingButtons.jsx';
import WebcamRenderer from '../components/WebcamRenderer.jsx';
import { selectStyles, stackStyles, formControlStyles } from './../themes';


const Acquisition = ({ setIsConfigChange, isConfigChange, config, setConfig }) => {
    // State variables
    

    const [selectedVideoDevices, setSelectedVideoDevices] = useState([]); // Selected video devices state
    const [selectedAudioDevice, setSelectedAudioDevice] = useState(''); // Selected audio device state
    const [videoDevices, setVideoDevices] = useState([]); // Video devices state
    const [audioDevices, setAudioDevices] = useState([]); // Audio devices state


    return (
        <div>
                <Stack sx={stackStyles}>
                    <Typography id="username" labelId="usernameLabel" variant="h6" >User: {config.username}</Typography>
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

                    {/* Stack for  material, and speed selection */}
                    <Stack sx={stackStyles} direction="row">
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
                                {config.chosenMaterials.filter(value => value !== 0).map((material) => (
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
                                {config.chosenSpeeds.filter(value => value !== 0).map((speeds) => (
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
