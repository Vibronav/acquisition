import Webcam from 'react-webcam';
import { Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';

const WebcamRenderer = ({ selectedVideoDevices, videoDevices }) => {

  const device = videoDevices.find(device => device.label === selectedVideoDevices[0]);
  
  switch (selectedVideoDevices.length) {
    case 0:
      return (
        <div style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, border: '2px dashed black', borderRadius: 5 }}>
          <p style={{ textAlign: 'center', fontSize: 24 }}>Select video device</p>
        </div>
      );
    case 1:
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: "20px" }}>
          {device && (
            <Stack>
              <Typography>{device.label}</Typography>
              <Webcam
                videoConstraints={{ deviceId: device.deviceId }}
                style={{ borderRadius: 5, width: '100%', height: 'auto' }}
              />
            </Stack>
          )}
          <div style={{ width: '50%', height: 400, border: '2px dashed black', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 5 }}>
            <p style={{ textAlign: 'center', fontSize: 24 }}>Select video device</p>
          </div>
        </div>
      );
    default:
      return (
        <div style={{ overflowX: 'auto', whiteSpace: 'nowrap', display: "flex", gap: "20px",  borderRadius: 5 }}>
          {selectedVideoDevices.map(label => {
            const device = videoDevices.find(device => device.label === label);
            if (device) {
              return (
                <Stack key={device.deviceId}>
                  <Typography>{device.label}</Typography>
                  <Webcam
                    videoConstraints={{ deviceId: device.deviceId }}
                    style={{ width: '100%', height: 400, borderRadius: 5 }}
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

WebcamRenderer.propTypes = {
  selectedVideoDevices: PropTypes.array.isRequired,
  videoDevices: PropTypes.array.isRequired,
}

export default WebcamRenderer;
