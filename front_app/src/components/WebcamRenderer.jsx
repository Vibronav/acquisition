import { Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { FormattedMessage } from 'react-intl';
import Webcam from 'react-webcam';

const WebcamRenderer = ({ selectedVideoDevices, videoDevices, webcamRef  }) => {

  const device = videoDevices.find(device => device.label === selectedVideoDevices[0]);

  
  switch (selectedVideoDevices.length) {
    case 0:
      return (
        <div style={{ width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400, border: '2px dashed black', borderRadius: 5 }}>
          <p style={{ textAlign: 'center', fontSize: 24 }}>
            {<FormattedMessage id="videoDeviceSelect"></FormattedMessage>}
          </p>
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
                screenshotFormat="image/jpeg"
                ref={webcamRef}
              />
            </Stack>
          )}
          <div style={{ width: '50%', height: 400, border: '2px dashed black', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 5 }}>
            <p style={{ textAlign: 'center', fontSize: 24 }}>
            {<FormattedMessage id="videoDeviceSelect"></FormattedMessage>}
            </p>
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
                    screenshotFormat="image/jpeg"
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
  webcamRef: PropTypes.object.isRequired
}

export default WebcamRenderer;
