import {
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Typography,
  Stack
} from '@mui/material';
import PropTypes from 'prop-types';
import { FormattedMessage } from 'react-intl';



const DobotController = ({ positionType, P1, P2, P3, numIterations, setP1, setP2, setP3, setPositionType, setNumIterations }) => {

  // JSX for the position fields
  const positionFields = (position, setPosition, label) => (
    <Stack sx={{ gap: 1}}>
      <Typography>{label}:</Typography>
      <Stack direction='row'>
        <TextField
          label="X"
          value={position.x}
          onChange={(e) => setPosition((prev) => ({ ...prev, x: e.target.value }))}

        />
        <TextField
          label="Y"
          value={position.y}
          onChange={(e) => setPosition((prev) => ({ ...prev, y: e.target.value }))}

        />
        <TextField
          label="Z"
          value={position.z}
          onChange={(e) => setPosition((prev) => ({ ...prev, z: e.target.value }))}
        />
      </Stack>
    </Stack>
  );

  // The UI rendering
  return (
    <Stack sx={{ border: "solid grey 2px", borderRadius: 5, padding: 3, gap: 3 }}>
      <Typography id="dobotInterface" labelId="dobotInterface" variant="h7" >
        <FormattedMessage id="dobotInterface" />
      </Typography>

      {/* <Grid item xs={12} sm={6}>
          <FormControl fullWidth>
            <InputLabel>Speed</InputLabel>
            <Select
              value={speed}
              onChange={(e) => setSpeed(e.target.value)}
            >
              {config.speeds.map((spd, idx) => (
                <MenuItem key={idx} value={spd}>
                  {spd}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid> */}


      <FormControl fullWidth>
        <InputLabel>Position Type</InputLabel>
        <Select
          value={positionType}
          onChange={(e) => setPositionType(e.target.value)}
        >
          <MenuItem value="Only Up and Down">Only Up and Down</MenuItem>
          <MenuItem value="Up, Down, Forward">Up, Down, Forward</MenuItem>
        </Select>
      </FormControl>


      <Stack sx={{gap: 2}}>

        {positionFields(P1, setP1, 'Up (P1)')}

        {positionFields(P2, setP2, 'Down (P2)')}

        {positionType === 'Up, Down, Forward' && (
          <>
            {positionFields(P3, setP3, 'Forward (P3)')}
          </>
        )}
      </Stack>


      <TextField
        label="Number of Iterations"
        value={numIterations}
        onChange={(e) => setNumIterations(e.target.value)}
        fullWidth
      />



    </Stack>
  );
};

DobotController.propTypes = {
  config: PropTypes.object.isRequired,
  positionType: PropTypes.string.isRequired,
  P1: PropTypes.string.isRequired,
  P2: PropTypes.string.isRequired,
  P3: PropTypes.string.isRequired,
  numIterations: PropTypes.string.isRequired,
  setP1: PropTypes.func.isRequired,
  setP2: PropTypes.func.isRequired,
  setP3: PropTypes.func.isRequired,
  setPositionType: PropTypes.func.isRequired,
  setNumIterations: PropTypes.func.isRequired
};

export default DobotController;