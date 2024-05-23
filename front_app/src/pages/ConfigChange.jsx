import React, { useState } from 'react';
import {
  Box,
  TextField,
  Stack,
  IconButton,
  OutlinedInput,
  InputAdornment,
  Typography,
  Button
} from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import MaterialsAndSpeeds from '../components/MaterialsAndSpeeds';

export default function ConfigChange({ setIsConfigChange, isConfigChange, config, setConfig }) {
  const [incorrectUsername, setIncorrectUsername] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleUsernameInput = (event) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      username: event.target.value
    }));
  };

  const handleClickShowPassword = () => setShowPassword((show) => !show);

  const handleMouseDownPassword = (event) => {
    event.preventDefault();
  };

  const handleSave = () => {
    const isUsernameIncorrect = config.username.indexOf("_") !== -1
      || config.username.length === 0
      || config.username.indexOf(" ") !== -1;

    setIncorrectUsername(isUsernameIncorrect);

    if (!isUsernameIncorrect) {
      setIsConfigChange(!isConfigChange);
    }
  };

  return (
    <Box >
      <Stack direction="row" gap={4} sx={{ marginTop: 5, width: "100%" }}>

        <Stack direction="row" gap={4} sx={{ width: "100%" }}>
          <Stack gap={2} sx={{ width: "100%" }} >
            <Stack gap={2}>
              <Typography variant="h6">Username</Typography>
              <TextField
                error={incorrectUsername}
                helperText={incorrectUsername ? "Incorrect entry." : ""}
                value={config.username}
                onChange={handleUsernameInput}
              />
            </Stack>
            <Stack gap={2} sx={{ width: "100%" }}>
              <Typography variant="h6">Saving Directory</Typography>
              <TextField label="Local Dir" defaultValue={config.local_dir} />
              <TextField label="Remote Dir" defaultValue={config.remote_dir} />
            </Stack>
          </Stack>

          <Stack gap={2} sx={{ width: "100%" }}>
            <Typography variant="h6">Connection</Typography>
            <TextField label="Device" defaultValue={config.connection[0]} />
            <TextField label="Port" defaultValue={config.connection[1]} />
            <TextField label="Username" defaultValue={config.connection[2]} />
            <OutlinedInput
              id="outlined-adornment-password"
              type={showPassword ? 'text' : 'password'}
              endAdornment={
                <InputAdornment position="end">
                  <IconButton
                    aria-label="toggle password visibility"
                    onClick={handleClickShowPassword}
                    onMouseDown={handleMouseDownPassword}
                    edge="end"
                  >
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              }
              label="Password"
              defaultValue={config.connection[3]}
            />
          </Stack>
        </Stack>

        <MaterialsAndSpeeds config={config} setConfig={setConfig} />
      </Stack>

      <Stack sx={{ width: "100%", alignItems: "end", marginTop: 7 }}>
        <Button onClick={handleSave} variant="contained">
          Save
        </Button>
      </Stack>
    </Box>
  );
}
