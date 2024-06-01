import SettingsIcon from '@mui/icons-material/Settings';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import PropTypes from 'prop-types';
import { useNavigate } from 'react-router-dom';
import { routes } from '../paths';
import ThemeSwitchButton from './ThemeSwitchButton';
export default function NavBar({ currentTheme, onChangeTheme }) {
  const navigate = useNavigate();

  const handleConfigChange = () => {
    navigate(routes['Home']);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar variant="dense">
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
