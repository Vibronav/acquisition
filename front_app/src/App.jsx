// Filename - App.js

import { Container, CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import React, { useEffect, useState } from 'react';
import { HashRouter, Route, Routes } from "react-router-dom";
import NavBar from './components/NavBar.jsx';
import defaultConfig from './defaultConfig';
import Acquisition from "./pages/Acquisition.jsx";
import ConfigChange from "./pages/ConfigChange.jsx";
import { routes } from './paths';
import { darkTheme, lightTheme } from './themes';



function App() {

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
        <HashRouter>
          <NavBar
            currentTheme={light}
            onChangeTheme={toggleTheme}
          />
          <Routes>
            <Route
              path={routes.Home}
              element={
                <Container maxWidth="lg" style={{ marginTop: '20px' }}>
                  <ConfigChange
                  config={config}
                  setConfig={setConfig} />
                </Container>
              }
            />
            <Route
              path={routes.Camera}
              element={
                <Container maxWidth="lg" style={{ marginTop: '20px' }}>
                  <Acquisition
                  config={config}
                  />
                </Container>
              }
            />
          </Routes>
        </HashRouter>
      </ThemeProvider>
    </React.Fragment>
  );
}

export default App;
