import { useState } from 'react';
import {  Select, Typography, Stack, InputLabel, MenuItem, FormControl } from '@mui/material';
import MenuIntroduction from '../components/CheckList.jsx';
import VideoAudioSelect from '../components/VideoAudioSelect.jsx'
import RecordingButtons from '../components/RecordingButtons.jsx';
import WebcamRenderer from '../components/WebcamRenderer.jsx';
import { selectStyles, stackStyles, formControlStyles } from './../themes';
import PropTypes from 'prop-types';


const Acquisition = ({ setIsConfigChange, isConfigChange, config, setConfig }) => {
    // State variables
    const [selectedVideoDevices, setSelectedVideoDevices] = useState([]); // Selected video devices state
    const [videoDevices, setVideoDevices] = useState([]); // Video devices state

    const [selectedMaterial, setSelectedMaterial] = useState(null);
    const [selectedSpeed, setSelectedSpeed] = useState(null);

    const handleMaterialChange = (event) =>{
        setSelectedMaterial(event.target.value)
    }

    const handleSpeedChange = (event) =>{
        setSelectedSpeed(event.target.value)
    }

    return (
        <div>
            <Stack sx={stackStyles}>
                <MenuIntroduction/>
                <Typography id="username" labelId="usernameLabel" variant="h6" >User: {config.username}</Typography>
                {/* Video and audio selection component */}
                <VideoAudioSelect
                    selectedVideoDevices={selectedVideoDevices}
                    setSelectedVideoDevices={setSelectedVideoDevices}
                    videoDevices={videoDevices}
                    setVideoDevices={setVideoDevices}
                    
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
                            value={selectedMaterial}
                            onChange={handleMaterialChange}

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
                            value={selectedSpeed}
                            onChange={handleSpeedChange}
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

                    <RecordingButtons username={config.username} material={selectedMaterial} speed={selectedSpeed}/>
                    {/* Component for rendering webcams */}
                    <WebcamRenderer selectedVideoDevices={selectedVideoDevices} videoDevices={videoDevices} />
                </Stack>

            </Stack>


        </div >
    );
}

Acquisition.propTypes = {
    setIsConfigChange: PropTypes.func.isRequired,
    isConfigChange: PropTypes.bool.isRequired,
    config: PropTypes.object.isRequired,
    setConfig: PropTypes.func.isRequired,
};

export default Acquisition;
