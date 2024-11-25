import { Stack, Typography } from '@mui/material';
import PropTypes from 'prop-types';
import { FormattedMessage } from 'react-intl';
import { useEffect, useState } from 'react';
import axiosInstance from '../../axiosConfig'; // Ensure this is your configured Axios instance

const CamRenderer = ({ selectedVideoDevices, videoDevices, webcamRef }) => {
  const [streamUrl, setStreamUrl] = useState(null);

  // Function to fetch video stream from the server
  const fetchStream = async (deviceId) => {
    try {
      // Make a POST request to the /stream endpoint with the selected camera index
      const response = await axiosInstance.post(
        '/stream',
        { cameraIndex: parseInt(deviceId) }, // Sending device index as required by your backend
        { responseType: 'blob' } // Expect a blob response (image stream)
      );

      // Create a URL for the received blob to use as an image source
      const blobUrl = URL.createObjectURL(response.data);
      setStreamUrl(blobUrl);
    } catch (error) {
      console.error('Error fetching video stream:', error);
    }
  };

  // Effect to fetch stream when a device is selected
  useEffect(() => {
    if (selectedVideoDevices.length === 1) {
      const device = videoDevices.find((device) => device.label === selectedVideoDevices[0]);
      if (device) {
        fetchStream(device.deviceId); // Fetch stream using the selected device's ID
      }
    }

    // Cleanup function to revoke the blob URL when the component unmounts or stream changes
    return () => {
      if (streamUrl) {
        URL.revokeObjectURL(streamUrl);
        setStreamUrl(null);
      }
    };
  }, [selectedVideoDevices, videoDevices, streamUrl]);

  // Determine the selected device based on the selected label
  const device = videoDevices.find((device) => device.label === selectedVideoDevices[0]);

  switch (selectedVideoDevices.length) {
    case 0:
      return (
        <div
          style={{
            width: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: 350,
            border: '2px dashed black',
            borderRadius: 5,
          }}
        >
          <p style={{ textAlign: 'center', fontSize: 24 }}>
            <FormattedMessage id="videoDeviceSelect" />
          </p>
        </div>
      );

    case 1:
      return (
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {device && (
            <Stack>
              <Typography>{device.label}</Typography>
              {streamUrl ? (
                <img
                  src={streamUrl}
                  alt="Camera Stream"
                  style={{ borderRadius: 5, width: '100%', height: 'auto' }}
                  ref={webcamRef}
                />
              ) : (
                <p>Loading stream...</p>
              )}
            </Stack>
          )}
          <div
            style={{
              width: '50%',
              height: 350,
              border: '2px dashed black',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 5,
            }}
          >
            <p style={{ textAlign: 'center', fontSize: 24 }}>
              <FormattedMessage id="videoDeviceSelect" />
            </p>
          </div>
        </div>
      );

    default:
      return (
        <div
          style={{
            overflowX: 'auto',
            whiteSpace: 'nowrap',
            display: 'flex',
            gap: '20px',
            borderRadius: 5,
          }}
        >
          {selectedVideoDevices.map((label) => {
            const device = videoDevices.find((device) => device.label === label);
            if (device) {
              return (
                <Stack key={device.deviceId}>
                  <Typography>{device.label}</Typography>
                  <img
                    src={streamUrl}
                    alt="Camera Stream"
                    style={{ width: '100%', height: 350, borderRadius: 5 }}
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

CamRenderer.propTypes = {
  selectedVideoDevices: PropTypes.array.isRequired,
  videoDevices: PropTypes.array.isRequired,
  webcamRef: PropTypes.object.isRequired,
};

export default CamRenderer;
