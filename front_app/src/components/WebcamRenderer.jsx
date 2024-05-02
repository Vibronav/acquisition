import React from 'react';
import Webcam from 'react-webcam';
import { Stack, Typography } from '@mui/material';

const WebcamRenderer = ({ selectedVideoDevices, videoDevices }) => {
  switch (selectedVideoDevices.length) {
    case 0:
      return (
        <div style={{ width: '50%', display: 'flex', justifyContent: 'center', alignItems: 'center', height: 430, border: '2px dashed black', borderRadius: 10 }}>
          <p style={{ textAlign: 'center', fontSize: 24 }}>Select video device</p>
        </div>
      );
    case 1:
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
            const device = videoDevices.find(device => device.label === label);
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
              return null;
            }
          })}
        </div>
      );
  }
};

export default WebcamRenderer;
