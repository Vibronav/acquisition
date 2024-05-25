// Filename - App.js

import React, { useEffect, useState } from 'react';
import { darkTheme, lightTheme } from './themes';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Container } from '@mui/material';
import NavBar from './components/NavBar.jsx';
import Acquisition from "./pages/Acquisition.jsx";
import ConfigChange from "./pages/ConfigChange.jsx";


const defaultConfig = {
  username: "",
  connection: ["raspberrypi", 22, "pi", "VibroNav"],
  defaultMaterials: [
    "Slime",
    "Silicone",
    "PU",
    "Plato (play dough)",
    "Plastic",
    "Ikea (plastic bag)",
    "African (silk)"
  ],
  chosenMaterials: [],
  newMaterials: [],
  defaultSpeeds: ["slow", "medium", "fast"],
  chosenSpeeds: [],
  newSpeeds: [],
  local_dir: "c:\\vnav_acquisition",
  remote_dir: "vnav_acquisition"

}

function App() {

  const [configChange, setConfigChange] = useState(true);
  const [light, setLight] = useState(false); // Theme state
  const storedConfig = JSON.parse(localStorage.getItem("config"));

  const initialConfig = storedConfig || defaultConfig;
  const [config, setConfig] = useState(initialConfig);

  // Toggle between light and dark themes
  const toggleTheme = () => {
    setLight((prevTheme) => !prevTheme);
  };

  useEffect(()=>{
    localStorage.setItem("config",JSON.stringify(config))
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
