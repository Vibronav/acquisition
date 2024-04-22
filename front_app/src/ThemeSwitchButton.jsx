import React from 'react';
import FormControl from '@mui/material/FormControl';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Switch from '@mui/material/Switch';
import DarkModeIcon from '@mui/icons-material/DarkMode';
import LightModeIcon from '@mui/icons-material/LightMode';

export default function ThemeSwitchButton({ currentTheme, onChange }) {
  const handleChange = () => {
    onChange(!currentTheme); // Toggle the theme and notify the parent component
  };

  return (
    <FormControl component="fieldset" variant="standard">
      <FormGroup>
        <FormControlLabel
          control={
            <Switch checked={currentTheme} onChange={handleChange} name="themeChange"/>
          }
          label={currentTheme ?   <LightModeIcon /> : <DarkModeIcon />} // Render DarkModeIcon for dark theme and LightModeIcon for light theme
        />
      </FormGroup>
    </FormControl>
  );
}
