import { useEffect } from 'react';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import ListItemText from '@mui/material/ListItemText';
import Select from '@mui/material/Select';
import Checkbox from '@mui/material/Checkbox';
import Stack from '@mui/material/Stack';
import { selectStyles, stackStyles, formControlStyles } from '../themes.js'




export default function VideoAudioSelect({
    selectedVideoDevices,
    setSelectedVideoDevices,
    selectedAudioDevice,
    setSelectedAudioDevice,
    videoDevices,
    setVideoDevices,
    audioDevices,
    setAudioDevices
}) {

    useEffect(() => {
        const fetchMediaDevices = async () => {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                const audioDevices = devices.filter(device => device.kind === 'audioinput');
                setVideoDevices(videoDevices);
                setAudioDevices(audioDevices);
            } catch (error) {
                console.error('Error fetching media devices:', error);
            }
        };

        fetchMediaDevices();
    }, []);

    const handleVideoDeviceChange = (event) => {
        setSelectedVideoDevices(event.target.value);
    };

    const handleAudioDeviceChange = (event) => {
        setSelectedAudioDevice(event.target.value);
    };

    return (
        <div>
            <Stack
                sx={stackStyles} direction="row" >
                <FormControl
                    sx={formControlStyles} >
                    <InputLabel id="video-devices-label">Video Devices</InputLabel>
                    <Select
                        sx={selectStyles}
                        labelId="video-devices-label"
                        id="video-devices"
                        multiple
                        value={selectedVideoDevices}
                        onChange={handleVideoDeviceChange}
                        renderValue={(selected) => selected.join(', ')}
                        label="Video Devices"
                    >
                        {videoDevices.map((device) => (
                            <MenuItem key={device.label} value={device.label}>
                                <Checkbox checked={selectedVideoDevices.includes(device.label)} />
                                <ListItemText primary={device.label} />
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <FormControl
                    sx={formControlStyles} >
                    <InputLabel id="audio-device-label">Audio Device</InputLabel>
                    <Select
                        sx={selectStyles}
                        labelId="audio-device-label"
                        id="audio-device"
                        value={selectedAudioDevice}
                        onChange={handleAudioDeviceChange}
                        label="Audio Device"
                    >
                        {audioDevices.map((device) => (
                            <MenuItem key={device.label} value={device.label}>
                                {device.label}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Stack>
        </div>
    );
}
