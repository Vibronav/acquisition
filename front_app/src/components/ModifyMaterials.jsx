import React from 'react';
import { Stack } from '@mui/material';
import PropTypes from 'prop-types';
import ConfigurableList from './ConfigurableList';

export default function ModifyMaterials({ config, setConfig }) {
  const [checkedMaterial, setCheckedMaterial] = React.useState(config.chosenMaterials);
  const [addedMaterials, setAddedMaterials] = React.useState(config.newMaterials);

  React.useEffect(() => {
    setCheckedMaterial(config.chosenMaterials);
    setAddedMaterials(config.newMaterials);
  }, [config]);

  React.useEffect(() => {
    setConfig(prevConfig => ({
      ...prevConfig,
      chosenMaterials: checkedMaterial,
      newMaterials: addedMaterials,
    }));
  }, [checkedMaterial, addedMaterials, setConfig]);

  return (
    <Stack sx={{ width: "100%" }}>
      <ConfigurableList
        title="Materials"
        addPrompt="Add material"
        defaultItems={config.defaultMaterials}
        addedItems={addedMaterials}
        setAddedItems={setAddedMaterials}
        checkedItems={checkedMaterial}
        setCheckedItems={setCheckedMaterial}
        height={460}
      />
    </Stack>

  );
}

ModifyMaterials.propTypes = {
  config: PropTypes.object.isRequired,
  setConfig: PropTypes.func.isRequired,
};
