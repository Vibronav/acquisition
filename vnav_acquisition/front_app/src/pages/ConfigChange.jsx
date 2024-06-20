import RestartAltIcon from '@mui/icons-material/RestartAlt';
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
  TextareaAutosize,
  Typography
} from '@mui/material';
import PropTypes from 'prop-types';
import { useState } from 'react';
import { FormattedMessage } from 'react-intl';
import { useNavigate } from 'react-router-dom';
import ModifyLabChecklist from '../components/ModifyLabChecklist';
import ModifyMaterials from '../components/ModifyMaterials';
import ModifySpeeds from '../components/ModifySpeeds';
import { routes } from '../paths';
import { useEffect } from 'react';

ConfigChange.propTypes = {
  config: PropTypes.object.isRequired,
  setConfig: PropTypes.func.isRequired,
  handleReset: PropTypes.func.isRequired
};

export default function ConfigChange({config, setConfig, handleReset }) {
  const [incorrectUsername, setIncorrectUsername] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const initalComment = sessionStorage.getItem('commentConfig') || '';
  const [comment, setComment] = useState(initalComment);
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
  }

  useEffect(() => {
    sessionStorage.setItem("commentConfig",comment)
  },[comment])

return (
  <Box >
    <Stack direction="row" gap={4} sx={{ marginTop: 5, width: "100%" }}>

      <Stack direction="row" gap={4} sx={{ width: "100%" }}>
        <Stack gap={2} sx={{ width: "100%" }} >
          <Stack gap={2}>
            <Typography variant="h6">
              {<FormattedMessage id="username"/>}
            </Typography>
            <TextField
              error={incorrectUsername}
              helperText={incorrectUsername ? "Incorrect entry." : ""}
              value={config.username}
              onChange={handleUsernameInput}
            />
          </Stack>

          <Stack gap={2} sx={{ width: "100%" }}>
            <Typography variant="h6">
              {<FormattedMessage id="connection"/>}
            </Typography>
            <TextField label={<FormattedMessage id="Device"/>} value={config.connection[0]} onChange={(e) => handleChangeConnection(0, e.target.value)} />
            <TextField label={<FormattedMessage id="Port"/>} value={config.connection[1]} onChange={(e) => handleChangeConnection(1, e.target.value)} />
            <TextField label={<FormattedMessage id="Device name"/>} value={config.connection[2]} onChange={(e) => handleChangeConnection(2, e.target.value)} />
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
            <Typography variant="h6">
              <FormattedMessage id="comment"/>
              <TextareaAutosize 
                style={{ width: '100%' }} 
                value={comment} 
                minRows={4}
                maxRows={10}
                onChange={(() => {setComment(event.target.value)})}
                />
            </Typography>
          </Stack>
        </Stack>

        <Stack gap={4} sx={{ width: "100%" }}>

          <Stack gap={2} sx={{ width: "100%" }}>
            <Typography variant="h6">
              {<FormattedMessage id="saveDir"/>}
            </Typography>
            <TextField label={<FormattedMessage id="LocalDir"/>} value={config.local_dir} onChange={handleChangeLocalDir} />
            <TextField label={<FormattedMessage id="RemoteDir"/>} value={config.remote_dir} onChange={handleChangeRemoteDir} />
          </Stack>
          <ModifyLabChecklist config={config} setConfig={setConfig} />
        
        </Stack>

        <ModifyMaterials config={config} setConfig={setConfig} />
        <ModifySpeeds config={config} setConfig={setConfig} />
      </Stack>

    </Stack>

    <Stack
      sx={{
        width: "100%",
        alignItems: "end",
        marginTop: 5,
        gap: 1,
        justifyContent: "flex-end"
      }}
      direction="row"
    >
      <Button onClick={handleReset} variant="contained">
        <RestartAltIcon></RestartAltIcon>
        {<FormattedMessage id="resetButton"/>}
      </Button>
      <Button onClick={handleSave} variant="contained" disabled={config.username == null || config.chosenMaterials.length == 0
        || config.chosenSpeeds.length == 0}>
        {<FormattedMessage id="saveButton"/>}
      </Button>

    </Stack>

  </Box>
);
}
