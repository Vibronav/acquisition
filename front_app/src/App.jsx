import React, { useState } from 'react';
import { Fragment } from "react";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl"; // Corrected import path
import WebcamStreamCapture from './VideoDisplay';
import darkTheme from './Theme';
import { ThemeProvider } from "@emotion/react";
import axios from 'axios';

function App() {
  const [response, setResponse] = useState(null);
  const [selectedMaterial, setSelectedMaterial] = useState(''); // Added state for selected material

  const handleChange = (event) => {
    setSelectedMaterial(event.target.value); // Update state on change
  };


  return (
    <ThemeProvider theme={darkTheme}>
      <Fragment >
        <FormControl sx={{ minWidth: 120 }}> 
          <InputLabel id="demo-simple-select-label">Material</InputLabel>
          <Select
            labelId="demo-simple-select-label"
            id="demo-simple-select"
            value={selectedMaterial} // Use state for selected value
            label="Material"
            onChange={handleChange}
          >
           <MenuItem value="Slime">Slime</MenuItem>
            <MenuItem value="Silicone">Silicone</MenuItem>
            <MenuItem value="PU">PU</MenuItem>
            <MenuItem value="Plato (play dough)">Plato (play dough)</MenuItem>
            <MenuItem value="Plastic">Plastic</MenuItem>
            <MenuItem value="Ikea (plastic bag)">Ikea (plastic bag)</MenuItem>
            <MenuItem value="African (silk)">African (silk)</MenuItem>

          </Select>
        </FormControl>

        <WebcamStreamCapture />
      </Fragment>
    </ThemeProvider>
  );
}

export default App;
