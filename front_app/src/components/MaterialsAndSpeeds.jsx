import * as React from 'react';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import AddIcon from '@mui/icons-material/Add';
import {
  FormControl,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  OutlinedInput,
  Typography,
  Stack,
  InputAdornment,
  InputLabel
} from '@mui/material';


export default function MaterialsAndSpeeds({ config, setConfig }) {
  const [newMaterial, setNewMaterial] = React.useState('');
  const [newSpeed, setNewSpeed] = React.useState('');
  const [checkedMaterial, setCheckedMaterial] = React.useState([0]);
  const [checkedSpeed, setCheckedSpeed] = React.useState([0]);
  const [addedMaterials, setAddedMaterials] = React.useState([]);
  const [addedSpeeds, setAddedSpeeds] = React.useState([]);

  const handleChooseMaterial = (value) => () => {
    const currentIndex = checkedMaterial.indexOf(value);
    const newCheckedMaterial = [...checkedMaterial];

    if (currentIndex === -1) {
      newCheckedMaterial.push(value);
    } else {
      newCheckedMaterial.splice(currentIndex, 1);
    }

    setCheckedMaterial(newCheckedMaterial); // Update checkedMaterial state with new value

    // Update chosenMaterials based on newCheckedMaterial
    setConfig(prevConfig => ({
      ...prevConfig,
      chosenMaterials: newCheckedMaterial // Replace with the updated checked material array
    }));
  };


  const handleNewMaterialInput = (event) => {
    setNewMaterial(event.target.value);
  };

  const handleAddMaterial = () => {
    if (!addedMaterials.includes(newMaterial)) {
      setAddedMaterials(prevAddedMaterials => [
        ...prevAddedMaterials,
        newMaterial
      ]);
    }
  };

  const handleDeleteMaterial = (material) => {
    setAddedMaterials(prevAddedMaterials =>
      prevAddedMaterials.filter(item => item !== material)
    );
  };


  const handleChooseSpeed = (value) => () => {
    const currentIndex = checkedSpeed.indexOf(value);
    const newCheckedSpeed = [...checkedSpeed];

    if (currentIndex === -1) {
      newCheckedSpeed.push(value);
    } else {
      newCheckedSpeed.splice(currentIndex, 1);
    }

    setCheckedSpeed(newCheckedSpeed); // Update checkedSpeed state with new value

    // Update chosenSpeeds based on newCheckedSpeed
    setConfig(prevConfig => ({
      ...prevConfig,
      chosenSpeeds: newCheckedSpeed // Replace with the updated checked speed array
    }));
  };

  const handleNewSpeedInput = (event) => {
    setNewSpeed(event.target.value);
  };

  const handleAddSpeed = () => {
    if (!addedSpeeds.includes(newSpeed)) {
      setAddedSpeeds(prevAddedSpeed => [
        ...prevAddedSpeed,
        newSpeed
      ]);
    }
  };

  const handleDeleteSpeed = (speed) => {
    setAddedSpeeds(prevAddedSpeeds =>
      prevAddedSpeeds.filter(item => item !== speed)
    );
  };

  return (
    <Stack direction="row" gap={10} >
      <Stack sx={{ width: "100%", gap: 3 }}>
        <Typography variant="h5">Materials</Typography>
        <FormControl >
          <InputLabel>Add Material</InputLabel>
          <OutlinedInput
            endAdornment={
              <InputAdornment position="end">
                <IconButton
                  onClick={handleAddMaterial}
                  edge="end"
                  sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                  <AddIcon sx={{ color: 'secondary.main' }} />
                </IconButton>

              </InputAdornment>
            }
            label="Add Material"
            value={newMaterial}
            onChange={handleNewMaterialInput}
          />


        </FormControl>
        <List sx={{ width: '100%', maxHeight: 400, overflow: 'auto', bgcolor: 'background.paper', borderRadius: 2 }}>
          {config.defaultMaterials.map((value) => {
            const labelId = `checkbox-list-label-${value}`;

            return (
              <ListItem
                key={value}
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleChooseMaterial(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checkedMaterial.indexOf(value) !== -1}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText id={labelId} primary={value} />
                </ListItemButton>
              </ListItem>
            );
          })}

          {addedMaterials.map((value) => {
            const labelId = `checkbox-list-label-${value}`;

            return (
              <ListItem
                key={value}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="comments"
                    onClick={() => handleDeleteMaterial(value)}
                    sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                    <DeleteOutlineIcon sx={{ color: 'secondary.main' }} />
                  </IconButton>
                }
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleChooseMaterial(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checkedMaterial.indexOf(value) !== -1}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText id={labelId} primary={value} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Stack>



      <Stack sx={{ width: "100%", gap: 3 }}>
        <Typography variant="h5">Speeds</Typography>
        <FormControl >
          <InputLabel>Add Speed</InputLabel>
          <OutlinedInput
            endAdornment={
              <InputAdornment position="end">
                <IconButton
                  onClick={handleAddSpeed}
                  edge="end"
                  sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                  <AddIcon sx={{ color: 'secondary.main' }} />
                </IconButton>

              </InputAdornment>
            }
            label="Add Speed"
            value={newSpeed}
            onChange={handleNewSpeedInput}
          />


        </FormControl>
        <List sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 2, maxHeight: 400, overflow: 'auto', }}>
          {config.defaultSpeeds.map((value) => {
            const labelId = `checkbox-list-label-${value}`;

            return (
              <ListItem
                key={value}
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleChooseSpeed(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checkedSpeed.indexOf(value) !== -1}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText id={labelId} primary={value} />
                </ListItemButton>
              </ListItem>
            );
          })}

          {addedSpeeds.map((value) => {
            const labelId = `checkbox-list-label-${value}`;

            return (
              <ListItem
                key={value}
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="comments"
                    onClick={() => handleDeleteSpeed(value)}
                    sx={{ '&:hover': { backgroundColor: '#f0f0f0' } }}>
                    <DeleteOutlineIcon sx={{ color: 'secondary.main' }} />
                  </IconButton>
                }
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleChooseSpeed(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checkedSpeed.indexOf(value) !== -1}
                      tabIndex={-1}
                      disableRipple
                      inputProps={{ 'aria-labelledby': labelId }}
                    />
                  </ListItemIcon>
                  <ListItemText id={labelId} primary={value} />
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Stack>
    </Stack>
  );

}
