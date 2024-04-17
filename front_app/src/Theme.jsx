import React, { Fragment } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import {CssBaseline} from '@mui/material';
import ThemeSwitchButton from './ThemeSwitchButton.jsx'

export default function Theme() {
  const [light, setLight] = React.useState(true);
  const darkTheme = createTheme({
    palette: {
      type: 'dark',
      background: {
        default: "#eeeeee"
      },
      primary: {
        main: '#035c23',
      },
      secondary: {
        main: '#c76492',
      },
    },
  });

  const lightTheme = createTheme({
    palette: {
      type: 'light',
      background: {
        default: "#aaaaaa"
      },
      primary: {
        main: '#035c23',
      },
      secondary: {
        main: '#c76492',
      },
    },
  });

  return (
    <div>
      <ThemeProvider theme={light ? lightTheme : darkTheme}>
      <CssBaseline />
      <ThemeSwitchButton onClick={() => setLight(prev => !prev)}>Toggle Theme</ThemeSwitchButton>
      </ThemeProvider>
    </div>
  );
}