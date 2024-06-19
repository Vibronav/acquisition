import React, { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useWavesurfer } from '@wavesurfer/react';
import { Button, CircularProgress, Stack } from '@mui/material';

const AudioPlayer = ({ audioUrl }) => {
    const containerRef = useRef(null);
    const { wavesurfer, isPlaying } = useWavesurfer({
        container: containerRef,
        height: 100,
        waveColor: '#c87000',
        progressGradient: '#dde5e0',
        url: audioUrl
    });

    const [isLoading, setIsLoading] = useState(true);
    const [initialLoad, setInitialLoad] = useState(true);

    useEffect(() => {
        if (wavesurfer) {
            wavesurfer.load(audioUrl);
            wavesurfer.on('ready', () => {
                setIsLoading(false); // Update loading state when ready
                if (initialLoad) {
                    setInitialLoad(false);
                }
                // Automatically start playing if desired
                // wavesurfer.play();
            });
        }
    }, [audioUrl, wavesurfer, initialLoad]);

    const onPlayPause = () => {
        if (wavesurfer) {
            wavesurfer.playPause();
        }
    };

    return (
        <Stack>
            <Button onClick={onPlayPause} disabled={isLoading || initialLoad} sx={{ width: 'min-content' }}>
                {isPlaying ? "Pause" : "Play"}
            </Button>
            {isLoading && (
                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}>
                    <CircularProgress size={24} /> {/* Loading indicator */}
                </div>
            )}
            <div ref={containerRef} />
        </Stack>
    );
};

AudioPlayer.propTypes = {
    audioUrl: PropTypes.string.isRequired
};

export default AudioPlayer;
