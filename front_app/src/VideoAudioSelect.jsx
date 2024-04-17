import * as React from 'react';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import ListItemText from '@mui/material/ListItemText';
import Select from '@mui/material/Select';
import Checkbox from '@mui/material/Checkbox';
import Stack from '@mui/material/Stack';



const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
    PaperProps: {
        style: {
            maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
            width: 250,
        },
    },
};

export default function VideoAudioSelect() {
    const [videoDevices, setVideoDevices] = React.useState([]);
    const [audioDevices, setAudioDevices] = React.useState([]);
    const [selectedVideoDevices, setSelectedVideoDevices] = React.useState([]);
    const [selectedAudioDevice, setSelectedAudioDevice] = React.useState('');

    React.useEffect(() => {
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
            <Stack direction="row">
                <FormControl sx={{  width: 300 }}>
                    <InputLabel id="video-devices-label">Video Devices</InputLabel>
                    <Select
                        labelId="video-devices-label"
                        id="video-devices"
                        multiple
                        value={selectedVideoDevices}
                        onChange={handleVideoDeviceChange}
                        renderValue={(selected) => selected.join(', ')}
                        MenuProps={MenuProps}
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
                <FormControl sx={{minWidth: 300 }}>
                    <InputLabel id="audio-device-label">Audio Device</InputLabel>
                    <Select
                        labelId="audio-device-label"
                        id="audio-device"
                        value={selectedAudioDevice}
                        onChange={handleAudioDeviceChange}
                        label="Audio Device"
                    >
                        {audioDevices.map((device) => (
                            <MenuItem key={device.deviceId} value={device.deviceId}>
                                {device.label}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Stack>
        </div>
    );
}
