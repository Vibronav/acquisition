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
  const [checked, setChecked] = React.useState([0]);
  const [newMaterial, setNewMaterial] = React.useState('');

  const handleToggle = (value) => () => {
    const currentIndex = checked.indexOf(value);
    const newChecked = [...checked];

    if (currentIndex === -1) {
      newChecked.push(value);
    } else {
      newChecked.splice(currentIndex, 1);
    }

    setChecked(newChecked);
  };

  const handleNewMaterialInput = (event) => {
    setNewMaterial(event.target.value);
  };

  const handleAddMaterial = () => {
    // Check if the new material already exists in the addedMaterials array
    if (!config.addedMaterials.includes(newMaterial)) {
      setConfig(prevConfig => ({
        ...prevConfig,
        addedMaterials: [...prevConfig.addedMaterials, newMaterial]
      }));
    }
  };

  const handleDeleteMaterial = (material) => {
    setConfig(prevConfig => ({
      ...prevConfig,
      addedMaterials: prevConfig.addedMaterials.filter(item => item !== material)
    }));
  };

  return (
    <Stack direction="row">
      <Stack sx={{ width: "100%" }}>
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
                  <AddIcon sx={{color: 'secondary.main'}}/>
                </IconButton>

              </InputAdornment>
            }
            label="Add Material"
            value={newMaterial}
            onChange={handleNewMaterialInput}
          />


        </FormControl>
        <List sx={{ width: '100%', maxWidth: 360, bgcolor: 'background.paper', borderRadius: 2 }}>
          {config.defaultMaterials.map((value) => {
            const labelId = `checkbox-list-label-${value}`;

            return (
              <ListItem
                key={value}
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleToggle(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checked.indexOf(value) !== -1}
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

          {config.addedMaterials.map((value) => {
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
                    <DeleteOutlineIcon sx={{color: 'secondary.main'}}/>
                  </IconButton>
                }
                disablePadding
              >
                <ListItemButton role={undefined} onClick={handleToggle(value)} dense>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={checked.indexOf(value) !== -1}
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
