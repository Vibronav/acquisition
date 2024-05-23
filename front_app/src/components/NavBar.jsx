import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import SettingsIcon from '@mui/icons-material/Settings';
import ThemeSwitchButton from './ThemeSwitchButton';
import PropTypes from 'prop-types';

export default function NavBar({ currentTheme, onChangeTheme, setIsConfigChange, isConfigChange }) {
  const handleConfigChange = () => {
    setIsConfigChange(true);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar variant="dense">
          {isConfigChange ?

            <Typography variant="h8" component="div" sx={{ flexGrow: 1 }}>
              Configuration Settings
            </Typography>
            :
            <>
              <IconButton
                size="small"
                edge="start"
                color="inherit"
                aria-label="menu"
                sx={{ mr: 2 }}
              >


                <SettingsIcon onClick={handleConfigChange} />
              </IconButton>
              <Typography variant="h8" component="div" sx={{ flexGrow: 1 }}>
                Change Configuration
              </Typography>
            </>
          }
          <ThemeSwitchButton currentTheme={currentTheme} onChange={onChangeTheme} />
        </Toolbar>
      </AppBar>
    </Box>
  );
}
NavBar.propTypes = {
  currentTheme: PropTypes.boolean,
  onChangeTheme: PropTypes.func.isRequired,
  setIsConfigChange: PropTypes.func.isRequired,
  isConfigChange: PropTypes.boolean
}
