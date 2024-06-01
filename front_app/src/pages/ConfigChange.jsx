import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import {
  Box,
  Button,
  IconButton,
  InputAdornment,
  OutlinedInput,
  Stack,
  TextField,
  Typography
} from '@mui/material';
import PropTypes from 'prop-types';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MaterialsAndSpeeds from '../components/MaterialsAndSpeeds';
import defaultConfig from '../defaultConfig';
import { routes } from '../paths';

ConfigChange.propTypes = {
  setIsConfigChange: PropTypes.func.isRequired,
  isConfigChange: PropTypes.bool.isRequired,
  config: PropTypes.object.isRequired,
  setConfig: PropTypes.func.isRequired,
};

export default function ConfigChange({config, setConfig }) {
  const [incorrectUsername, setIncorrectUsername] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();


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
      navigate(routes['Camera']);
    }
    
  };

  const handleReset = () => {
    setConfig(defaultConfig);
  }

  const handleChangeLocalDir = (event) => {
    const newLocalDir = event.target.value;
    setConfig((prevConfig) => ({
      ...prevConfig,
      local_dir: newLocalDir,
    }));
  };

  const handleChangeRemoteDir = (event) => {
    const newLocalDir = event.target.value;
    setConfig((prevConfig) => ({
      ...prevConfig,
      remote_dir: newLocalDir,
    }));
  };

  const handleChangeConnection = (index, value) => {
    const newConnection = [...config.connection];
    newConnection[index] = value;
    setConfig((prevConfig) => ({
      ...prevConfig,
      connection: newConnection,
    }));
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
              <TextField label="Local Dir" value={config.local_dir} onChange={handleChangeLocalDir}/>
              <TextField label="Remote Dir" value={config.remote_dir} onChange={handleChangeRemoteDir}/>
            </Stack>
          </Stack>

          <Stack gap={2} sx={{ width: "100%" }}>
            <Typography variant="h6">Connection</Typography>
            <TextField label="Device" value={config.connection[0]} onChange={(e) => handleChangeConnection(0, e.target.value)}/>
            <TextField label="Port" value={config.connection[1]} onChange={(e) => handleChangeConnection(1, e.target.value)}/>
            <TextField label="Username" value={config.connection[2]}onChange={(e) => handleChangeConnection(2, e.target.value)} />
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
              value={config.connection[3]}
              onChange={(e) => handleChangeConnection(3, e.target.value)}
            />
          </Stack>
        </Stack>

        <MaterialsAndSpeeds config={config} setConfig={setConfig} />
      </Stack>

      <Stack sx={{ width: "100%", alignItems: "end", marginTop: 7, gap: 1 }}>
        {console.log(config.chosenSpeeds.is)}
        <Button onClick={handleSave} variant="contained" disabled={config.username == null || config.chosenMaterials.length == 0
           || config.chosenSpeeds.length == 0}>
          Save
        </Button>
        <Button onClick={handleReset} variant="contained">
          Reset
        </Button>
      </Stack>
    </Box>
  );
}
