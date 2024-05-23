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
    <FormControl component="fieldset" variant="standard" >
      <FormGroup>
        <FormControlLabel
          control={
            <Switch 
            checked={currentTheme} 
            onChange={handleChange} 
            name="themeChange" 
            size="small" 
            sx={{backgroundColor: 'rgb(255,255,255,0.5)', borderRadius:20}}/>
          }
          label={currentTheme ?   <LightModeIcon fontSize="small"/> : <DarkModeIcon fontSize="small"/>} // Render DarkModeIcon for dark theme and LightModeIcon for light theme
        />
      </FormGroup>
    </FormControl>
  );
}
