// Filename - App.js

import React, { useState } from 'react';
import { darkTheme, lightTheme } from './themes';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Container, Stack } from '@mui/material';
import NavBar from './components/NavBar.jsx';
import Acquisition from "./pages/Acquisition.jsx";
import ConfigChange from "./pages/ConfigChange.jsx";


function App() {

  const [configChange, setConfigChange] = useState(true);
  const [light, setLight] = useState(false); // Theme state
  const [config, setConfig] = useState([]);

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setLight((prevTheme) => !prevTheme);
  };

  return (
    <React.Fragment>
      <ThemeProvider theme={light ? lightTheme : darkTheme}>
        <CssBaseline /> {/* Apply CSS baseline */}

        <NavBar
          currentTheme={light}
          onChangeTheme={toggleTheme}
          setIsConfigChange={setConfigChange}
          isConfigChange={configChange}
        />



        <Container maxWidth="lg" style={{ marginTop: '20px' }}>
          <Stack spacing={10}>
            {configChange ?
                <ConfigChange 
                setIsConfigChange={setConfigChange} 
                isConfigChange={configChange} 
                config={config} 
                setConig={setConfig}/> 
              :
                <Acquisition 
                  setIsConfigChange={setConfigChange} 
                  isConfigChange={configChange} 
                  config={config} 
                  /> 
              }
          </Stack>
        </Container>
      </ThemeProvider>
    </React.Fragment>
  );
}

export default App;
