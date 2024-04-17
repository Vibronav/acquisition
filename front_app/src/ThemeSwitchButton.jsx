// ThemeSwitchButton.jsx
import React from 'react';
import FormControl from '@mui/material/FormControl';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormHelperText from '@mui/material/FormHelperText';
import Switch from '@mui/material/Switch';

export default function ThemeSwitchButton({ currentTheme, onChange }) {
  const handleChange = () => {
    onChange(!currentTheme); // Toggle the theme and notify the parent component
  };

  return (
    <FormControl component="fieldset" variant="standard">
      <FormGroup>
        <FormControlLabel
          control={
            <Switch checked={currentTheme} onChange={handleChange} name="themeChange" />
          }
          label = {currentTheme? "Light Mode" : "Dark Mode"}
        />
      </FormGroup>
    </FormControl>
  );
}
