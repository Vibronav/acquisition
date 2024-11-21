import Checkbox from '@mui/material/Checkbox';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import ListItemText from '@mui/material/ListItemText';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Stack from '@mui/material/Stack';
import PropTypes from 'prop-types';
import { useEffect } from 'react';
import { FormattedMessage } from 'react-intl';
import { formControlStyles, selectStyles, stackStyles } from '../themes.js';


export default function VideoAudioSelect({
    selectedVideoDevices,
    setSelectedVideoDevices,
    videoDevices,
    setVideoDevices
}) {

    useEffect(() => {
        const fetchMediaDevices = async () => {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                setVideoDevices(videoDevices);
            } catch (error) {
                console.error('Error fetching media devices:', error);
            }
        };

        fetchMediaDevices();
    }, []);

    const handleVideoDeviceChange = (event) => {
        setSelectedVideoDevices(event.target.value);
    };


    return (
        <div>
            <Stack
                sx={stackStyles} direction="row"  >
                <FormControl
                    sx={formControlStyles} >
                    <InputLabel id="video-devices-label">
                        {<FormattedMessage id="videoDevices"></FormattedMessage>}
                    </InputLabel>
                    <Select
                        sx={selectStyles}
                        labelId="video-devices-label"
                        id="video-devices"
                        multiple
                        value={selectedVideoDevices}
                        onChange={handleVideoDeviceChange}
                        renderValue={(selected) => selected.join(', ')}
                        label={<FormattedMessage id="videoDevices"></FormattedMessage>}
                    >
                        {videoDevices.map((device) => (
                            <MenuItem key={device.label} value={device.label}>
                                <Checkbox checked={selectedVideoDevices.includes(device.label)} />
                                <ListItemText primary={device.label} />
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                
            </Stack>
        </div>
    );
}

VideoAudioSelect.propTypes = {
    selectedVideoDevices: PropTypes.array.isRequired,
    setSelectedVideoDevices: PropTypes.func.isRequired,
    videoDevices: PropTypes.array.isRequired,
    setVideoDevices: PropTypes.func.isRequired
}