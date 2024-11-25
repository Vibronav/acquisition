import { useState } from 'react';
import SettingsIcon from '@mui/icons-material/Settings';
import { MenuItem, Select, Button } from '@mui/material';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import PropTypes from 'prop-types';
import { FormattedMessage, useIntl } from 'react-intl';
import { useNavigate } from 'react-router-dom';
import { routes } from '../paths';
import KeyboardShortcutsHelp from './KeyboardShortcutsHelp';
import ThemeSwitchButton from './ThemeSwitchButton';

export default function NavBar({ currentTheme, onChangeTheme, changeLanguage }) {
  const navigate = useNavigate();


  const handleConfigChange = () => {
    navigate(routes['Home']);
  };


  const intl = useIntl();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar variant="dense">

          <IconButton
            size="small"
            edge="start"
            color="inherit"
            aria-label="menu"
            
            onClick={handleConfigChange}
          >
            <SettingsIcon sx={{ mr: 1 }} />
            <Typography  component="div" >
            {<FormattedMessage id="configurationChange" />}
          </Typography>
          </IconButton>
          

          
          <Box sx={{ flexGrow: 1 }}></Box>

          <KeyboardShortcutsHelp></KeyboardShortcutsHelp>
          <ThemeSwitchButton currentTheme={currentTheme} onChange={onChangeTheme} />
          <Select
            value={intl.locale}
            onChange={changeLanguage}
          >
            <MenuItem value="en"><FormattedMessage id="en" /></MenuItem>
            <MenuItem value="pl"><FormattedMessage id="pl" /></MenuItem>
            <MenuItem value="de"><FormattedMessage id="de" /></MenuItem>
          </Select>
        </Toolbar>
      </AppBar>
    </Box>
  );
}

NavBar.propTypes = {
  currentTheme: PropTypes.boolean,
  onChangeTheme: PropTypes.func.isRequired,
  setIsConfigChange: PropTypes.func.isRequired,
  changeLanguage: PropTypes.func.isRequired
}
