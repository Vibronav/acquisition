import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';
import Button from '@mui/material/Button';
import { TextField, FormControl, Stack } from '@mui/material';
import MaterialsAndSpeeds from '../components/MaterialsAndSpeeds';

export default function ConfigChange({ setIsConfigChange, isConfigChange, config, setConfig }) {
  const [activeStep, setActiveStep] = useState(0);
  const [incorrectUsername, setIncorrectUsername] = useState(false);

  const steps = ['Username', 'Connection settings', 'Add materials and speeds', 'Saving directory selection'];


  const handleNext = () => {
    setActiveStep(prevActiveStep => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep(prevActiveStep => prevActiveStep - 1);
  };

  const handleFinish = () => {
    setIsConfigChange(!isConfigChange);
  };

  const handleUsernameInput = (event) => {
    setConfig((prevConfig) => ({
      ...prevConfig,
      username: event.target.value
    }));
  };

  const handleUsernameCheck = () => {
    if (config.username.indexOf("_") !== -1 || config.username.length === 0) {
      setIncorrectUsername(true);
    } else {
      setIncorrectUsername(false);
      handleNext();
    }
  };

  const stepContent = [
    // Content for step 0 (Username)
    <Stack gap={2}>
      <FormControl>
        <TextField
          label="Username"
          error={incorrectUsername}
          helperText={incorrectUsername ? "Incorrect entry." : ""}
          value={config.username}
          onChange={handleUsernameInput}
        />
      </FormControl>
    </Stack>,

    // Content for step 1 (Connection settings)

    <Stack gap={2}>
      <FormControl>
        <TextField label="Device" defaultValue={config.connection[0]}/>
      </FormControl>
      <FormControl>
        <TextField label="Port" defaultValue="22" />
      </FormControl>
      <FormControl>
        <TextField label="?" defaultValue="pi" />
      </FormControl>
      <FormControl>
        <TextField label="?" defaultValue="VibroNav" />
      </FormControl>
    </Stack>,

    // Content for step 2 (Add materials and speeds)
    
      <MaterialsAndSpeeds config={config} setConfig={setConfig} />
    ,

    // Content for step 3 (Saving directory selection)
    <Stack gap={2}>
      <FormControl>
        <TextField label="Local Dir" defaultValue={config.local_dir} />
      </FormControl>
      <FormControl>
        <TextField label="Remote Dir" defaultValue={config.remote_dir}  />
      </FormControl>
    </Stack>,
  ];

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper activeStep={activeStep} sx={{ paddingBottom: 5 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {stepContent[activeStep]}

      <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
        <Button
          color="inherit"
          disabled={activeStep === 0}
          onClick={handleBack}
          sx={{ mr: 1 }}
        >
          Back
        </Button>
        <Box sx={{ flex: '1 1 auto' }} />
        {activeStep === steps.length - 1 ? (
          <Button onClick={handleFinish}>Finish</Button>
        ) : (
          <Button onClick={activeStep === 0 ? handleUsernameCheck : handleNext}>
            Next
          </Button>
        )}
      </Box>
    </Box>
  );
}
