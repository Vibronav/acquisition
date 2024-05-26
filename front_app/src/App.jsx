// Filename - App.js

import { Container, CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import React, { useEffect, useState } from 'react';
import NavBar from './components/NavBar.jsx';
import defaultConfig from './defaultConfig';
import Acquisition from "./pages/Acquisition.jsx";
import ConfigChange from "./pages/ConfigChange.jsx";
import { darkTheme, lightTheme } from './themes';



function App() {

  const [configChange, setConfigChange] = useState(true);
  const [light, setLight] = useState(false); // Theme state
  const storedConfig = JSON.parse(sessionStorage.getItem("config"));

  const initialConfig = storedConfig || defaultConfig;
  const [config, setConfig] = useState(initialConfig);

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setLight((prevTheme) => !prevTheme);
  };

  useEffect(()=>{
    sessionStorage.setItem("config",JSON.stringify(config))
  },[config])
  
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

          {configChange ?
            <ConfigChange
              setIsConfigChange={setConfigChange}
              isConfigChange={configChange}
              config={config}
              setConfig={setConfig} />
            :
            <Acquisition
              setIsConfigChange={setConfigChange}
              isConfigChange={configChange}
              config={config}
              setConfig={setConfig}
            />
          }

        </Container>
      </ThemeProvider>
    </React.Fragment>
  );
}

export default App;
