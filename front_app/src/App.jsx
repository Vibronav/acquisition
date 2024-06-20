// Filename - App.js

import { Container, CssBaseline } from '@mui/material';
import { ThemeProvider } from '@mui/material/styles';
import React, { Suspense, lazy, useEffect, useState } from 'react';
import { IntlProvider } from "react-intl";
import { HashRouter, Route, Routes } from "react-router-dom";
import { useConfig } from '../api/requests.js';
import messagesDe from "../src/languages/de.json";
import messagesEn from "../src/languages/en.json";
import messagesPl from "../src/languages/pl.json";
import LoadingBar from './components/LoadingBar.jsx';
import NavBar from './components/NavBar.jsx';
import { routes } from './paths';
import { darkTheme, lightTheme } from './themes';
import { ErrorBoundary } from 'react-error-boundary';
const ConfigChange = lazy(() => import("./pages/ConfigChange.jsx"))
const Acquisition = lazy(() => import("./pages/Acquisition.jsx"))

const messages = {
  'en': messagesEn,
  'pl': messagesPl,
  'de': messagesDe,
}

function App() {

  const [locale, setLocale] = useState(() => {
    const stored = sessionStorage.getItem("language");
    const userLang = navigator.language;
  
    return stored || userLang.substring(0, 2);
  });

  const changeLocale = (newLocale) => {
    setLocale(newLocale.target.value);
    sessionStorage.setItem("language", newLocale.target.value.toString());
  };

  const [light, setLight] = useState(false); // Theme state

  const toggleTheme = () => {
    setLight((prevTheme) => !prevTheme);
  };

  const { data: axiosConfig, isLoading } = useConfig();
  const [config, setConfig] = useState(null);

  useEffect(() => {
    const storedConfig = JSON.parse(sessionStorage.getItem("config"));
    if (!isLoading && storedConfig === null) {
      setConfig(axiosConfig);
    } else {
      setConfig(storedConfig);
    }
  }, [isLoading, axiosConfig]);

  useEffect(() => {
    if (config != null){
      sessionStorage.setItem("config", JSON.stringify(config));
    }
  }, [config]);
  
  const handleReset = () => {
    setConfig(axiosConfig)
  }

  return (
    <IntlProvider locale={locale.toString()} messages={messages[locale]}>
      <React.Fragment>
        <ThemeProvider theme={light ? lightTheme : darkTheme}>
          <CssBaseline /> {/* Apply CSS baseline */}
          <HashRouter>
            <NavBar
              currentTheme={light}
              onChangeTheme={toggleTheme}
              changeLanguage={changeLocale}
            />
            <Routes>
              <Route
                path={routes.Home}
                element={
                  <Container maxWidth="lg" style={{ marginTop: '20px' }}>
                  {config === null ? (
                    <LoadingBar/>
                  ) : (
                    <ErrorBoundary fallback={<div>ups</div>}>
                      <Suspense fallback={<LoadingBar/>}>
                        <ConfigChange
                        config={config}
                        setConfig={setConfig}
                        handleReset={handleReset}
                      />
                      </Suspense>
                    </ErrorBoundary>
                  )}
                  </Container>
                }
              />
              <Route
                path={routes.Camera}
                element={
                  <Container maxWidth="lg" style={{ marginTop: '20px' }}>
                    {config === null ? (
                    <LoadingBar/>
                  ) : (
                      <ErrorBoundary fallback={<div>ups</div>}>
                        <Suspense fallback={<LoadingBar/>}>
                          <Acquisition
                          config={config}
                          />
                        </Suspense>
                      </ErrorBoundary>)}
                  </Container>
                }
              />
            </Routes>
          </HashRouter>
        </ThemeProvider>
      </React.Fragment>
    </IntlProvider>
  );
}

export default App;
